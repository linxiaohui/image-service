# -*- coding: utf-8 -*-
# 基于[DeepMosaic项目](https://github.com/HypoX64/DeepMosaics)进行剪裁
# 使用项目提供的预训练模型进行图片风格的迁移

import os
import sys
import imghdr

import zerorpc
import numpy as np
import cv2

from util import Opt
from models import loadmodel, runmodel


class DeepMosaic_Style(object):
    def style_transfer(self, image_data, style):
        """
        style:
            apple2orange
            orange2apple
            summer2winter
            winter2summer.pth'
            cezanne
            monet
            ukiyoe
            vangogh
        """
        image_type = imghdr.what(None, image_data)
        opt = Opt()
        opt.model_path = os.path.join("pretrained_models", f"style_{style}.pth")
        netG = loadmodel.style(opt)
        img = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        print("image loaded")
        img = runmodel.run_styletransfer(opt, netG, img)
        print("transfered")
        is_success, im_buf_arr = cv2.imencode("."+image_type, img)
        byte_im = im_buf_arr.tobytes()
        return byte_im

if __name__ == "__main__":
    s = zerorpc.Server(DeepMosaic_Style())
    s.bind("tcp://0.0.0.0:54332")
    s.run()

