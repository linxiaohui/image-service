# -*- coding: utf-8 -*-
"""
将keras h5模型转换为ONNX模型后(见`to_onnx.py`)，使用OpenCV进行推理，获取图片的NSFW值
"""
import io
import os

import cv2
import zerorpc
import numpy as np
from PIL import Image

class NSFWCV2(object):
    """使用OpenCV DNN加载ONNX模型并进行推理"""
    def __init__(self):
        MODEL_DIR = os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'nsfw.onnx')
        self.model = cv2.dnn.readNetFromONNX(MODEL_DIR)
        self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

    def nsfw_score(self, image_data):
        # 根据Keras版本的步骤对数据进行预处理
        image_bytes = io.BytesIO(image_data)
        img = Image.open(image_bytes)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.resize((299, 299), Image.NEAREST)
        img_np = np.asarray(img, dtype=np.float32)
        img_np /= 255
        img_np = np.asarray([img_np])
        self.model.setInput(img_np)
        out = self.model.forward()
        categories = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']


if __name__ == "__main__":
    s = zerorpc.Server(NSFWCV2())
    s.bind("tcp://0.0.0.0:54322")
    s.run()
