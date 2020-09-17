# -*- coding: utf-8 -*-
import os
import json

import zerorpc


from beauty_predict import beauty_predict

class ImageService(object):
    def beauty_score(self, image_data, image_ext='jpg'):
        return beauty_predict(image_data, image_ext)

s = zerorpc.Server(ImageService())
s.bind("tcp://0.0.0.0:54321")
s.run()


