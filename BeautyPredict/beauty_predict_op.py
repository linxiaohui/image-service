# -*- coding: utf-8 -*-
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import warnings
warnings.filterwarnings("ignore")
import imghdr

import numpy as np
import cv2
import dlib
from keras.models import Sequential
from keras.applications.resnet50 import ResNet50
from keras.layers import Dense

class BeautyPredictOp(object):
    def __init__(self):
        self.dlib_model_path = os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'mmod_human_face_detector.dat')
        self.resnet_model_path = os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'model-ldl-resnet.h5')
        self.resnet50_model_path = os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5')
        self.cnn_face_detector = dlib.cnn_face_detection_model_v1(self.dlib_model_path)
        self.resnet = ResNet50(include_top=False, pooling='avg', weights=self.resnet50_model_path)
        self.model = Sequential()
        self.model.add(self.resnet)
        self.model.add(Dense(5, activation='softmax'))
        self.model.layers[0].trainable = False
        self.model.load_weights(self.resnet_model_path)

    def score_mapping(self, model_score):
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

    def beauty_predict(self, img_data):
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
        dets = self.cnn_face_detector(im, 0)
        scores = []
        for i, d in enumerate(dets):
            face = [d.rect.left(), d.rect.top(), d.rect.right(), d.rect.bottom()]
            croped_im = im[face[1]:face[3], face[0]:face[2], :]
            resized_im = cv2.resize(croped_im, (224, 224))
            normed_im = np.array([(resized_im - 127.5) / 127.5])
            pred = self.model.predict(normed_im)
            ldList = pred[0]
            out = 1 * ldList[0] + 2 * ldList[1] + 3 * ldList[2] + 4 * ldList[3] + 5 * ldList[4]
            out = self.score_mapping(out)
            scores.append(out)
            cv2.rectangle(im, (face[0], face[1]), (face[2], face[3]), (0, 255, 0), 3)
            cv2.putText(im, str('%.2f' % out), (face[0], face[3]), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2)
        is_success, im_buf_arr = cv2.imencode("."+ext, im)
        byte_im = im_buf_arr.tobytes()
        return scores, byte_im
