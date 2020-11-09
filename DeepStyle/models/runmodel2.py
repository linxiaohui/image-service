import cv2
import sys
sys.path.append("..")
import torch
import numpy as np

from util import data

def run_styletransfer(opt, net, img):
    if opt.output_size != 0:
        if 'resize' in opt.preprocess and 'resize_scale_width' not in opt.preprocess:
            h, w = img.shape[:2]
            if w >= h:
                img = cv2.resize(img,(int(opt.output_size*w/h), opt.output_size),interpolation=cv2.INTER_LINEAR)
            else:
                img = cv2.resize(img,(opt.output_size, int(opt.output_size*h/w)),interpolation=cv2.INTER_LINEAR)
        elif 'resize_scale_width' in opt.preprocess:
            img = cv2.resize(img, (opt.output_size,opt.output_size))
        img = img[0:4*int(img.shape[0]/4),0:4*int(img.shape[1]/4),:]

    if 'edges' in opt.preprocess:
        if opt.canny > 100:
            canny_low = opt.canny-50
            canny_high = np.clip(opt.canny+50,0,255)
        elif opt.canny < 50:
            canny_low = np.clip(opt.canny-25,0,255)
            canny_high = opt.canny+25
        else:
            canny_low = opt.canny-int(opt.canny/2)
            canny_high = opt.canny+int(opt.canny/2)
        img = cv2.Canny(img,opt.canny-50,opt.canny+50)
        if opt.only_edges:
            return img
        img = data.im2tensor(img,use_gpu=opt.use_gpu,gray=True,use_transform = False,is0_1 = False)
    else:    
        img = data.im2tensor(img,use_gpu=opt.use_gpu,gray=False,use_transform = True)
    img = net(img)
    img = data.tensor2im(img)
    return img
