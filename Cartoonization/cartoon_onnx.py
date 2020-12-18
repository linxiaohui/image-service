# -*- coding: utf-8 -*-
"""
根据[White-box-Cartoonization](https://github.com/SystemErrorWang/White-box-Cartoonization/)中提供的预训练模型（checkpoints）
转换为pb(见`chkpt2pb.py`)
转换为ONNX模型后(使用tf2onnx)，使用ONNX进行推理，生成卡通化的图片
"""
import os
import imghdr

import zerorpc
import onnxruntime
import numpy as np
import cv2

def resize_crop(image):
    h, w, c = image.shape
    if h > 720 or w > 720:
        if h > w:
            h, w = int(720*h/w), 720
        else:
            h, w = 720, int(720*w/h)
    image = cv2.resize(image, (w, h), interpolation=cv2.INTER_AREA)
    h, w = (h//8)*8, (w//8)*8
    image = image[:h, :w, :]
    return image


class ONNXModel(object):
    def __init__(self, onnx_path=os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'cartoon.onnx')):
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
        # 输入数据的类型必须与模型一致,以下三种写法都是可以的
        # scores, boxes = self.onnx_session.run(None, {self.input_name: image_numpy})
        # scores, boxes = self.onnx_session.run(self.output_name, input_feed={self.input_name: image_numpy})
        input_feed = self.get_input_feed(self.input_name, image_numpy)
        out = self.onnx_session.run(self.output_name, input_feed=input_feed)
        return out

    def cartoon(self, image_data):
        """
        进行预处理，调用ONNX推理函数，生成结果图片
        """
        im = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        image = resize_crop(im)
        batch_image = image.astype(np.float32)/127.5 - 1
        batch_image = np.expand_dims(batch_image, axis=0)
        output = self.forward(batch_image)
        output = (np.squeeze(output)+1)*127.5
        output = np.clip(output, 0, 255).astype(np.uint8)
        ext = imghdr.what(None, image_data)
        is_success, im_buf_arr = cv2.imencode("."+ext, output)
        byte_im = im_buf_arr.tobytes()
        return byte_im


if __name__ == "__main__":
    # with open("x.jpg", "rb") as fp:
    #     dat = fp.read()
    # s = ONNXModel()
    # r = s.cartoon(dat)
    # with open("rz.jpg", "wb") as fp:
    #     fp.write(r)
    s = zerorpc.Server(ONNXModel())
    s.bind("tcp://0.0.0.0:54331")
    s.run()
