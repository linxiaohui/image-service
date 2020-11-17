import sys

import cv2
import torch
import numpy as np


sys.path.append("..")
import util.image_processing as impro
from util import data

def run_segment(img,net,size = 360,use_gpu = 0):
    img = impro.resize(img,size)
    img = data.im2tensor(img,use_gpu = use_gpu,  bgr2rgb = False,use_transform = False , is0_1 = True)
    mask = net(img)
    mask = data.tensor2im(mask, gray=True,rgb2bgr = False, is0_1 = True)
    return mask

def get_ROI_position(img,net,opt,keepsize=True):
    mask = run_segment(img,net,size=360,use_gpu = -1)
    mask = impro.mask_threshold(mask,opt.mask_extend,opt.mask_threshold)
    if keepsize:
        mask = impro.resize_like(mask, img)
    x,y,halfsize,area = impro.boundingSquare(mask, 1)
    return mask,x,y,halfsize,area

