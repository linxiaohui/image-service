# -*- coding: utf-8 -*-
import io
import time

import cv2
import zerorpc

from run import process


def infer_image_type(image_data):
    """根据图片的内容推断图片的格式"""
    if image_data[:8] == b'\x89PNG\r\n\x1a\n':
        return ".png"
    if image_data[:2] == b'\xff\xd8':
        return ".jpg"
    return ".jpg"

def strip_it(image_data):
    ext = infer_image_type(image_data)
    fn = "{}{}".format(time.time(), ext)
    with open(fn, "wb") as fp:
        fp.write(image_data)
    dress = cv2.imread(fn)
    h = dress.shape[0]
    w = dress.shape[1]
    dress = cv2.resize(dress, (512,512), interpolation=cv2.INTER_CUBIC)
    watermark = process(dress)
    watermark = cv2.resize(watermark, (w,h), interpolation=cv2.INTER_CUBIC)
    is_success, im_buf_arr = cv2.imencode(ext, watermark)
    byte_im = im_buf_arr.tobytes()
    return byte_im


class StripIt(object):
    def strip(self, image_data):
        return strip_it(image_data)

if __name__ == "__main__":
    s = zerorpc.Server(StripIt())
    s.bind("tcp://0.0.0.0:54328")
    s.run()
