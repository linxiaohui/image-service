# -*- coding: utf-8 -*-
""""
将预训练模型转换为ONNX格式，使用OpenCV读取并进行推理
"""
import os
import io
import time
import imghdr

import dlib
import cv2
import numpy as np
import zerorpc
from PIL import Image

dlib_model_path = os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'mmod_human_face_detector.dat')
cnn_face_detector = dlib.cnn_face_detection_model_v1(dlib_model_path)

def score_mapping(model_score):
    if model_score <= 1.9:
        mappingScore = ((4 - 2.5) / (1.9 - 1.0)) * (model_score-1.0) + 2.5
    elif model_score <= 2.8:
        mappingScore = ((5.5 - 4) / (2.8 - 1.9)) * (model_score-1.9) + 4
    elif model_score <= 3.4:
        mappingScore = ((6.5 - 5.5) / (3.4 - 2.8)) * (model_score-2.8) + 5.5
    elif model_score <= 4:
        mappingScore = ((8 - 6.5) / (4 - 3.4)) * (model_score-3.4) + 6.5
    elif model_score < 5:
        mappingScore = ((9 - 8) / (5 - 4)) * (model_score-4) + 8
    return mappingScore

class BeautyPredictCV2(object):
    def __init__(self):
        MODEL_DIR = os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'beauty-predict-fix.onnx')
        self.model = cv2.dnn.readNetFromONNX(MODEL_DIR)
        self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

    def beauty_score(self, img_data):
        ext = imghdr.what(None, img_data)
        im0 = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
        if im0.shape[0] > 1280:
            new_shape = (1280, im0.shape[1] * 1280 / im0.shape[0])
        elif im0.shape[1] > 1280:
            new_shape = (im0.shape[0] * 1280 / im0.shape[1], 1280)
        elif im0.shape[0] < 640 or im0.shape[1] < 640:
            new_shape = (im0.shape[0] * 2, im0.shape[1] * 2)
        else:
            new_shape = im0.shape[0:2]
        im = cv2.resize(im0, (int(new_shape[1]), int(new_shape[0])))
        dets = cnn_face_detector(im, 0)
        scores = []
        for i, d in enumerate(dets):
            face = [d.rect.left(), d.rect.top(), d.rect.right(), d.rect.bottom()]
            croped_im = im[face[1]:face[3], face[0]:face[2], :]
            resized_im = cv2.resize(croped_im, (224, 224))
            normed_im = np.array([(resized_im - 127.5) / 127.5])
            self.model.setInput(normed_im)
            pred = self.model.forward()
            ldList = pred[0]
            out = 1 * ldList[0] + 2 * ldList[1] + 3 * ldList[2] + 4 * ldList[3] + 5 * ldList[4]
            out = score_mapping(out)
            scores.append(out)
        return scores

if __name__ == "__main__":
    with open("x.jpg", "rb") as fp:
        dat = fp.read()
    s = BeautyPredictCV2()
    r = s.beauty_score(dat)
    print(r)
    # s = zerorpc.Server(FaceSketcherCV2())
    # s.bind("tcp://0.0.0.0:54325")
    # s.run()
              

