# -*- coding: utf-8 -*-
"""
根据https://cuijiahua.com/blog/2020/11/ai-7.html中提供的预训练模型，
转换为ONNX模型后(见`to_onnx.py`)，使用ONNX进行推理，生成人物肖像画
"""
import io
import os

import zerorpc
import onnxruntime
import numpy as np
from PIL import Image

class NSFWonnxModel(object):
    def __init__(self, onnx_path=os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'nsfw.onnx')):
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
        ONNX推理：注意其格式需要与模型一致
        image_numpy = [np.newaxis, img_height, img_width, img_chanel]
        onnx_session.run([output_name], {input_name: x})
        """
        # 输入数据的类型必须与模型一致,以下三种写法都是可以的
        # scores, boxes = self.onnx_session.run(None, {self.input_name: image_numpy})
        # scores, boxes = self.onnx_session.run(self.output_name, input_feed={self.input_name: image_numpy})
        input_feed = self.get_input_feed(self.input_name, image_numpy)
        out = self.onnx_session.run(self.output_name, input_feed=input_feed)
        return out

    def nsfw_score(self, image_data):
        """
        根据NSFW中的方法对图片进行预处理，调用ONNX推理函数，生成NSFW值
        """
        # 根据Keras版本的步骤对数据进行预处理
        image_bytes = io.BytesIO(image_data)
        img = Image.open(image_bytes)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.resize((299, 299), Image.NEAREST)
        img_np = np.asarray(img, dtype=np.float32)
        img_np /= 255
        img_np = np.asarray([img_np])
        out = self.forward(img_np)
        categories = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']
        print(out, "out")
        return out

if __name__ == "__main__":
    with open("x.jpg", "rb") as fp:
        dat = fp.read()
    s = NSFWonnxModel()
    r = s.nsfw_score(dat)
    print(r)

