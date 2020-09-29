#-*- coding:UTF-8 -*-
# 实现原理:把图像上某个像素点一定范围邻域内的所有点用邻域内随机选取的一个像素点的颜色代替
import io

import numpy as np
import cv2


def infer_image_type(image_data):
    """根据图片的内容推断图片的格式"""
    if image_data[:8] == b'\x89PNG\r\n\x1a\n':
        return ".png"
    if image_dta[:2] == b'\xff\xd8':
        return ".jpg"
    return ".jpg"

def domosaic(image_data, region, pixsize=5):
    """输入图片数据和进行马赛克的区域，返回马赛克后的图片数据"""
    image_type = infer_image_type(image_data[:20])
    (left, upper, width, hight) = region
    im = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    roi = im[upper:upper+hight,left:left+width]
    xstep = width//pixsize
    ystep = hight//pixsize
    for i in range(ystep):
        for j in range(xstep):
            roi[i*pixsize:i*pixsize+pixsize,j*pixsize:j*pixsize+pixsize]=roi[i*pixsize+pixsize//2,j*pixsize+pixsize//2]
    im[upper:upper+hight,left:left+width] = roi
    is_success, im_buf_arr = cv2.imencode(image_type, im)
    byte_im = im_buf_arr.tobytes()
    return byte_im


