# -*- coding: utf-8 -*-
"""
基于[DeepMosaics项目](https://github.com/HypoX64/DeepMosaics)提供的面部区域的预训练模型；
转换为ONNX格式使用OpenCV读取并进行推理
"""

import os
import imghdr

import cv2
import numpy as np
import zerorpc

class FaceMarkerCV2(object):
    def __init__(self):
        MODEL_DIR = os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'face.onnx')
        self.model = cv2.dnn.readNetFromONNX(MODEL_DIR)
        self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

    def face_marker(self, image_data):
        image_type = imghdr.what(None, image_data)
        image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        # 调整图片的大小
        img = cv2.resize(image, (360, 360), interpolation=cv2.INTER_LINEAR)
        # DeepMosaics中的im2tensor
        img = img / 255.0
        img = img.transpose((2, 0, 1))
        img = img[np.newaxis, :, :, :]
        # 执行模型推理
        self.model.setInput(img)
        image_numpy = self.model.forward()
        # DeepMosaics项目中的tensor2im
        image_numpy = image_numpy[0].astype(np.float32)
        image_numpy = np.clip(image_numpy * 255.0, 0, 255)
        h, w = image_numpy.shape[1:]
        image_numpy = image_numpy.reshape(h, w)
        mask = image_numpy.astype(np.uint8)
        # OpenCV处理
        mask = cv2.threshold(mask, 64, 255, cv2.THRESH_BINARY)[1]
        mask = cv2.blur(mask, (10, 10))
        mask = cv2.threshold(mask, 64/5, 255, cv2.THRESH_BINARY)[1]
        old_h, old_w = image.shape[:2]
        mask = cv2.resize(mask, (old_w, old_h))
        x, y, w, h = cv2.boundingRect(mask)
        # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        # OpenCV 4, findContours返回两个值
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        img = cv2.drawContours(image, contours, -1, (0, 255, 0), 3)
        is_success, im_buf_arr = cv2.imencode("."+image_type, img)
        byte_im = im_buf_arr.tobytes()
        return byte_im

if __name__ == "__main__":
    s = zerorpc.Server(FaceMarkerCV2())
    s.bind("tcp://0.0.0.0:54334")
    s.run()
