# -*- coding: utf-8 -*-
import os
import io
import time
import imghdr

import numpy as np
import cv2
import zerorpc

class FaceDetector(object):
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades,
                                                               "haarcascade_frontalface_default.xml")
        )
        self.factor = 1

    def face_mark(self, image_data):
        ext = imghdr.what(None, image_data)
        fn = "{}.{}".format(time.time(), ext)
        with open(fn, "wb") as fp:
            fp.write(image_data)
        img = cv2.imread(fn)
        img = cv2.resize(img, None, fx=self.factor, fy=self.factor, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            img = cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        is_success, im_buf_arr = cv2.imencode("."+ext, img)
        byte_im = im_buf_arr.tobytes()
        return byte_im

if __name__ == "__main__":
    s = zerorpc.Server(FaceDetector())
    s.bind("tcp://0.0.0.0:54324")
    s.run()
