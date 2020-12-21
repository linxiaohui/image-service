# -*- coding: utf-8 -*-
# 基于[DeepMosaic项目](https://github.com/HypoX64/DeepMosaics)进行剪裁
# 使用项目提供的预训练模型对图片的ROI区域进行标注
import os
import sys
import imghdr

import cv2
import torch
import numpy as np
import zerorpc

from dm_models import runmodel
from dm_models.BiSeNet_model import BiSeNet

class FaceMarkerOp(object):
    def __init__(self):
        self.netF = BiSeNet(num_classes=1, context_path='resnet18',train_flag=False)
        self.netF.load_state_dict(torch.load(os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'pretrained_models', 'add_face.pth')))
        self.netF.eval()

    def roi_marker(self, image_data):
        opt = Opt()
        image_type = imghdr.what(None, image_data)
        img = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        mask, (x, y, w, h) = runmodel.get_ROI_position(img, self.netF, opt)
        # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        # OpenCV 4, findContours返回两个值
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        img = cv2.drawContours(img, contours, -1, (0, 255, 0), 3)
        is_success, im_buf_arr = cv2.imencode("."+image_type, img)
        byte_im = im_buf_arr.tobytes()
        return byte_im

class Opt(object):
    """DeepMosaics的默认参数"""
    def __init__(self):
        self.mask_extend = 10
        self.mask_threshold = 64
        self.mosaic_mod = 'squa_avg'
        self.mosaic_size = 0

if __name__ == "__main__":
    s = zerorpc.Server(FaceMarkerOp())
    s.bind("tcp://0.0.0.0:54334")
    s.run()