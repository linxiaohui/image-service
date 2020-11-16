import os
import sys
import random

import cv2
import torch
import numpy as np
import torchvision.transforms as transforms


transform = transforms.Compose([  
    transforms.ToTensor(),  
    transforms.Normalize(mean = (0.5, 0.5, 0.5), std = (0.5, 0.5, 0.5))  
    ]  
)  

def tensor2im(image_tensor, imtype=np.uint8, gray=False, rgb2bgr = True ,is0_1 = False):
    image_tensor =image_tensor.data
    image_numpy = image_tensor[0].cpu().float().numpy()
    
    if not is0_1:
        image_numpy = (image_numpy + 1)/2.0
    image_numpy = np.clip(image_numpy * 255.0,0,255) 

    # gray -> output 1ch
    if gray:
        h, w = image_numpy.shape[1:]
        image_numpy = image_numpy.reshape(h,w)
        return image_numpy.astype(imtype)

    # output 3ch
    if image_numpy.shape[0] == 1:
        image_numpy = np.tile(image_numpy, (3, 1, 1))
    image_numpy = image_numpy.transpose((1, 2, 0))  
    if rgb2bgr and not gray:
        image_numpy = image_numpy[...,::-1]-np.zeros_like(image_numpy)
    return image_numpy.astype(imtype)


def im2tensor(image_numpy, imtype=np.uint8, gray=False,bgr2rgb = True, reshape = True, use_gpu = 0,  use_transform = True,is0_1 = True):
    
    if gray:
        h, w = image_numpy.shape
        image_numpy = (image_numpy/255.0-0.5)/0.5
        image_tensor = torch.from_numpy(image_numpy).float()
        if reshape:
            image_tensor = image_tensor.reshape(1,1,h,w)
    else:
        h, w ,ch = image_numpy.shape
        if bgr2rgb:
            image_numpy = image_numpy[...,::-1]-np.zeros_like(image_numpy)
        if use_transform:
            image_tensor = transform(image_numpy)
        else:
            if is0_1:
                image_numpy = image_numpy/255.0
            else:
                image_numpy = (image_numpy/255.0-0.5)/0.5
            image_numpy = image_numpy.transpose((2, 0, 1))
            image_tensor = torch.from_numpy(image_numpy).float()
        if reshape:
            image_tensor = image_tensor.reshape(1,ch,h,w)
    if use_gpu != -1:
        image_tensor = image_tensor.cuda()
    return image_tensor




def img_resize(img,size,interpolation=cv2.INTER_LINEAR):
    '''
    cv2.INTER_NEAREST      最邻近插值点法
    cv2.INTER_LINEAR        双线性插值法
    cv2.INTER_AREA         邻域像素再取样插补
    cv2.INTER_CUBIC        双立方插补，4*4大小的补点
    cv2.INTER_LANCZOS4     8x8像素邻域的Lanczos插值
    '''
    h, w = img.shape[:2]
    if np.min((w,h)) ==size:
        return img
    if w >= h:
        res = cv2.resize(img,(int(size*w/h), size),interpolation=interpolation)
    else:
        res = cv2.resize(img,(size, int(size*h/w)),interpolation=interpolation)
    return res


def run_segment(img,net,size = 360,use_gpu = 0):
    img = img_resize(img,size)
    img = im2tensor(img,use_gpu = use_gpu,  bgr2rgb = False,use_transform = False , is0_1 = True)
    mask = net(img)
    mask = tensor2im(mask, gray=True,rgb2bgr = False, is0_1 = True)
    return mask

def get_ROI_position(img,net,opt,keepsize=True):
    mask = run_segment(img,net,size=360,use_gpu = -1)
    mask = cv2.threshold(mask,opt.mask_threshold,255,cv2.THRESH_BINARY)[1]
    mask = cv2.blur(mask, (opt.mask_extend, opt.mask_extend))
    mask = cv2.threshold(mask,opt.mask_threshold/5,255,cv2.THRESH_BINARY)[1]
    if keepsize:
        h, w = img.shape[:2]
        mask = cv2.resize(mask, (w,h))
    x,y,w,h = cv2.boundingRect(mask)
    return mask, (x,y,w,h)

