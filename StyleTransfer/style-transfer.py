# -*- coding:utf-8 -*-
"""
参考 https://www.cvpy.net/studio/cv/func/DeepLearning/style_transfer/style_transfer/page/ 中的介绍，
使用OpenCV加载预训练模型，进行图片风格迁移
"""
import os
import imghdr

import cv2
import numpy as np
import zerorpc

MODELS_PATH = os.path.join(os.environ['IMAGESERVICE_ROOT'], "models")

STYLE_TRANS_MODLES = {}

def get_model_from_style(style):
    """
    加载指定风格的模型
    :param style: 模型的名称
    :return: model
    """
    if style in STYLE_TRANS_MODLES:
        return STYLE_TRANS_MODLES[style]
    if style in ["candy", "feathers", "la_muse",  "mosaic", "the_scream", "udnie"]:
        SUBPATH = "instance_norm"
    else:
        SUBPATH = "eccv16"
    model_path = os.path.join(MODELS_PATH, SUBPATH, style+".t7")
    model = cv2.dnn.readNetFromTorch(model_path)
    model = setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    STYLE_TRANS_MODLES[style] = model
    return model

net = get_model_from_style(3)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)


def transfer_stype(image_data, style):
    ext = imghdr.what(None, image_data)
    im = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    (h, w) = img.shape[:2]
    blob = cv2.dnn.blobFromImage(img, 1.0, (w, h), (103.939, 116.779, 123.680), swapRB=False, crop=False)
    net = get_model_from_style(style)
    net.setInput(blob)
    output = net.forward()
    # reshape输出结果, 将减去的平均值加回来，并交换各颜色通道
    output = output.reshape((3, output.shape[2], output.shape[3]))
    output[0] += 103.939
    output[1] += 116.779
    output[2] += 123.680
    output = output.transpose(1, 2, 0)
    is_success, im_buf_arr = cv2.imencode(ext, im)
    byte_im = im_buf_arr.tobytes()



class StyleTransfer(object):
    def style_transfer(self, image_data):
        return transfer_stype(image_data)


if __name__ == "__main__":
    s = zerorpc.Server(StyleTransfer())
    s.bind("tcp://0.0.0.0:54330")
    s.run()

