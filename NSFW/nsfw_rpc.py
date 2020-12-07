# -*- coding: utf-8 -*-
import os
import json

import zerorpc

from nsfw_predict import nsfw_predict
from nsfw_predict import nsfw_batch_predict

class ImageService(object):
    def nsfw_predict(self, image_data):
        ret = nsfw_predict(image_data)
        print(ret)
        return ret
    def nsfw_batch_predict(self, images):
        ret = nsfw_batch_predict(images)
        print(ret)
        return ret

s = zerorpc.Server(ImageService())
s.bind("tcp://0.0.0.0:54322")
s.run()


