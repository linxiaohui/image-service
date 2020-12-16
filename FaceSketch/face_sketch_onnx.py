# -*- coding: utf-8 -*-
"""
根据https://cuijiahua.com/blog/2020/11/ai-7.html中提供的预训练模型，
转换为ONNX模型后(见`to_onnx.py`)，使用ONNX进行推理，生成人物肖像画
"""
import io
import os
import imghdr

import zerorpc
import skimage.io
import skimage.transform
import onnxruntime
import numpy as np
from PIL import ImageOps
from PIL import Image

# normalize the predicted SOD probability map
def norm_pred(d):
    ma = np.max(d)
    mi = np.min(d)
    dn = (d-mi)/(ma-mi)
    return dn

class ONNXModel(object):
    def __init__(self, onnx_path=os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'sketch.onnx')):
        self.onnx_session = onnxruntime.InferenceSession(onnx_path)
        self.input_name = self.get_input_name()
        self.output_name = self.get_output_name()
        print("input_name:{}".format(self.input_name))
        print("output_name:{}".format(self.output_name))

    def get_output_name(self):
        output_name = []
        for node in self.onnx_session.get_outputs():
            output_name.append(node.name)
        return output_name

    def get_input_name(self):
        input_name = []
        for node in self.onnx_session.get_inputs():
            input_name.append(node.name)
        return input_name

    def get_input_feed(self, input_name, image_numpy):
        input_feed = {}
        for name in input_name:
            input_feed[name] = image_numpy
        return input_feed

    def forward(self, image_numpy):
        """
        ONNX推理：其中image_numpy格式
        image_numpy = image.transpose(2, 0, 1)
        image_numpy = image_numpy[np.newaxis, :]
        # onnx_session.run([output_name], {input_name: x})
        """
        # 输入数据的类型必须与模型一致,以下三种写法都是可以的
        # scores, boxes = self.onnx_session.run(None, {self.input_name: image_numpy})
        # scores, boxes = self.onnx_session.run(self.output_name, input_feed={self.input_name: image_numpy})
        input_feed = self.get_input_feed(self.input_name, image_numpy)
        out = self.onnx_session.run(self.output_name, input_feed=input_feed)
        return out

    def gen_output(self, image_data, pred):
        """
        根据模型输出生成结果图片（人物肖像画）
        """
        ext = imghdr.what(None, image_data)
        predict = pred
        predict = predict.squeeze()
        predict_np = predict.squeeze()
        # predict_np 的类型为 numpy.ndarray， shape=(320, 320)
        im = Image.fromarray(predict_np*255).convert('RGB')
        # im 的类型为 PIL.Image.Image， size=(320, 320)
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
        """
        根据U-2-Net中的方法对图片进行预处理，调用ONNX推理函数，生成结果图片
        """
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
        out, *_ = self.forward(tmpImg)
        pred = out[:, 0, :, :]
        pred = norm_pred(pred)
        dat = self.gen_output(image_data, pred)
        return dat

if __name__ == "__main__":
    # with open("x.jpg", "rb") as fp:
    #     dat = fp.read()
    # s = ONNXModel()
    # r = s.face_sketch(dat)
    # with open("rz.jpg", "wb") as fp:
    #     fp.write(r)
    s = zerorpc.Server(ONNXModel())
    s.bind("tcp://0.0.0.0:54325")
    s.run()
