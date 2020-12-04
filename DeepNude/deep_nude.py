# -*- coding: utf-8 -*-
import io
import time
import imghdr

import cv2
import zerorpc

from run import process

def strip_it(image_data):
    ext = imghdr.what(None, image_data)
    dress = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    h = dress.shape[0]
    w = dress.shape[1]
    dress = cv2.resize(dress, (512,512), interpolation=cv2.INTER_CUBIC)
    watermark = process(dress)
    watermark = cv2.resize(watermark, (w,h), interpolation=cv2.INTER_CUBIC)
    is_success, im_buf_arr = cv2.imencode("."+ext, watermark)
    byte_im = im_buf_arr.tobytes()
    return byte_im


class StripIt(object):
    def strip(self, image_data):
        return strip_it(image_data)

if __name__ == "__main__":
    s = zerorpc.Server(StripIt())
    s.bind("tcp://0.0.0.0:54328")
    s.run()
