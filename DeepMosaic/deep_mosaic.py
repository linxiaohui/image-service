# -*- coding: utf-8 -*-
# 基于[DeepMosaic项目](https://github.com/HypoX64/DeepMosaics)进行剪裁
# 使用项目提供的预训练模型对图片进行打码
import os
import sys
import imghdr

import cv2
import torch
import numpy as np
import zerorpc

from util import mosaic
from dm_models import runmodel
from dm_models.BiSeNet_model import BiSeNet

netF = BiSeNet(num_classes=1, context_path='resnet18',train_flag=False)
netX = BiSeNet(num_classes=1, context_path='resnet18',train_flag=False)
netF.load_state_dict(torch.load(os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'pretrained_models', 'add_face.pth')))
netX.load_state_dict(torch.load(os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'pretrained_models', 'add_youknow.pth')))
netF.eval()
netX.eval()
# 不使用GPU
# netF.cuda()
# netX.cuda()

class Opt(object):
    """DeepMosaics的默认参数"""
    def __init__(self):
        self.mask_extend = 10
        self.mask_threshold = 64
        self.mosaic_mod = 'squa_avg'
        self.mosaic_size = 0

class DeepMosaics_Mosaic(object):
    def deep_mosaic(self, image_data, roi_type='face'):
        opt = Opt()
        image_type = imghdr.what(None, image_data)
        img = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        if roi_type == 'face':
            netS = netF
        else:
            netS = netX
        mask = runmodel.get_ROI_position(img, netS, opt)[0]
        img = mosaic.addmosaic(img, mask, opt)
        is_success, im_buf_arr = cv2.imencode("."+image_type, img)
        byte_im = im_buf_arr.tobytes()
        return byte_im


if __name__ == "__main__":
    s = zerorpc.Server(DeepMosaics_Mosaic())
    s.bind("tcp://0.0.0.0:54333")
    s.run()
