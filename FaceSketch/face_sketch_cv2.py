# -*- coding: utf-8 -*-
""""
基于[U-2-Net项目](https://github.com/NathanUA/U-2-Net)的u2net_test.py文件修改
将预训练模型转换为ONNX格式(见`to_onnx.py`)，使用OpenCV读取并进行推理
"""
import os
import io
import imghdr

import skimage.io
import skimage.transform
import cv2
import numpy as np
import zerorpc
from PIL import Image
from PIL import ImageOps

# normalize the predicted SOD probability map
def norm_pred(d):
    ma = np.max(d)
    mi = np.min(d)
    dn = (d-mi)/(ma-mi)
    return dn

class FaceSketcherCV2(object):
    def __init__(self):
        MODEL_DIR = os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'sketch.onnx')
        self.model = cv2.dnn.readNetFromONNX(MODEL_DIR)
        self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

    def gen_output(self, image_data, pred):
        ext = imghdr.what(None, image_data)
        predict = pred
        predict = predict.squeeze()
        predict_np = predict.squeeze()
        # predict_np 的类型为 numpy.ndarray， shape=(512, 512)
        im = Image.fromarray(predict_np*255).convert('RGB')
        # im 的类型为 PIL.Image.Image， size=(512, 512)
        image = skimage.io.imread(io.BytesIO(image_data))
        # image 的类型为 numpy.ndarray， shape=(height,width, channel)
        # ori = Image.open(image_name)
        # ori的类型为 PIL.JpegImagePlugin.JpegImageFile， size=(width, height)
        imo = im.resize((image.shape[1], image.shape[0]), resample=Image.BILINEAR)
        imo = ImageOps.invert(imo)
        b = io.BytesIO()
        imo.save(b, ext)
        data = b.getvalue()
        return data

    def face_sketch(self, image_data):
        image_bytes = io.BytesIO(image_data)
        image = skimage.io.imread(image_bytes)
        image = skimage.transform.resize(image, (512, 512), mode='constant')
        tmpImg = np.zeros((image.shape[0], image.shape[1], 3))
        image = image / np.max(image)
        tmpImg[:, :, 0] = (image[:, :, 0] - 0.485) / 0.229
        tmpImg[:, :, 1] = (image[:, :, 1] - 0.456) / 0.224
        tmpImg[:, :, 2] = (image[:, :, 2] - 0.406) / 0.225
        tmpImg = tmpImg.transpose((2, 0, 1))
        tmpImg = tmpImg[np.newaxis, :, :, :]
        tmpImg = tmpImg.astype(np.float32)
        self.model.setInput(tmpImg)
        out = self.model.forward('1883')
        pred = out[:, 0, :, :]
        pred = norm_pred(pred)
        dat = self.gen_output(image_data, pred)
        return dat

if __name__ == "__main__":
    # with open("x.jpg", "rb") as fp:
    #     dat = fp.read()
    # s = FaceSketcherCV2()
    # r = s.face_sketch(dat)
    # with open("rz.jpg", "wb") as fp:
    #     fp.write(r)
    s = zerorpc.Server(FaceSketcherCV2())
    s.bind("tcp://0.0.0.0:54325")
    s.run()
