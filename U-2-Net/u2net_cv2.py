# -*- coding: utf-8 -*-
""""
基于[U-2-Net项目](https://github.com/NathanUA/U-2-Net)项目
将预训练模型转换为ONNX格式，使用OpenCV读取并进行推理
"""
import os
import io

import skimage
import skimage.io
import skimage.transform
import cv2
import zerorpc
import numpy as np
from PIL import Image

# normalize the predicted SOD probability map
def norm_pred(d):
    ma = np.max(d)
    mi = np.min(d)
    dn = (d-mi)/(ma-mi)
    return dn

class U2NetCV2(object):
    def __init__(self):
        MODEL_DIR = os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'u2net.onnx')
        self.model = cv2.dnn.readNetFromONNX(MODEL_DIR)
        self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

    def gen_mask(self, image_data, pred):
        predict = pred
        predict_np = predict.squeeze()
        im = Image.fromarray(predict_np*255).convert('RGB')
        image = skimage.io.imread(io.BytesIO(image_data))
        imo = im.resize((image.shape[1], image.shape[0]), resample=Image.BILINEAR)
        b = io.BytesIO()
        imo.save(b, "png")
        data = b.getvalue()
        return data

    def gen_output(self, image_data, pred):
        predict = pred
        predict_np = predict.squeeze()
        # predict_np 的类型为 numpy.ndarray， shape=(320, 320)
        im = Image.fromarray(predict_np*255).convert('RGB')
        # im 的类型为 PIL.Image.Image， size=(320, 320)
        image = skimage.io.imread(io.BytesIO(image_data))
        # image 的类型为 numpy.ndarray， shape=(height,width, channel)
        # ori = Image.open(image_name)
        # ori的类型为 PIL.JpegImagePlugin.JpegImageFile， size=(width, height)
        imo = im.resize((image.shape[1], image.shape[0]), resample=Image.BILINEAR)
        mask = np.asarray(imo)
        # mask 类型为 numpy.ndarray，元素为 np.uint8, shape=(height,width, channel)
        result = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
        result[:, :, 0] = image[:, :, 0]
        result[:, :, 1] = image[:, :, 1]
        result[:, :, 2] = image[:, :, 2]
        result[:, :, 3] = mask[:, :, 0]
        imo = Image.fromarray(np.uint8(result)).convert("RGBA")
        b = io.BytesIO()
        imo.save(b, "png")
        data = b.getvalue()
        return data

    def image_cutout(self, image_data):
        image_bytes = io.BytesIO(image_data)
        image = skimage.io.imread(image_bytes)
        image = skimage.transform.resize(image, (320, 320), mode='constant')
        tmpImg = np.zeros((image.shape[0], image.shape[1], 3))
        image = image / np.max(image)
        tmpImg[:, :, 0] = (image[:, :, 0] - 0.485) / 0.229
        tmpImg[:, :, 1] = (image[:, :, 1] - 0.456) / 0.224
        tmpImg[:, :, 2] = (image[:, :, 2] - 0.406) / 0.225
        tmpImg = tmpImg.transpose((2, 0, 1))
        tmpImg = tmpImg[np.newaxis, :, :, :]
        self.model.setInput(tmpImg)
        out = self.model.forward()
        pred = norm_pred(out)
        dat = self.gen_output(image_data, pred)
        return dat

if __name__ == "__main__":
    s = zerorpc.Server(U2NetCV2())
    s.bind("tcp://0.0.0.0:54323")
    s.run()


