# -*- coding: utf-8 -*-

import zerorpc

s = zerorpc.Client(heartbeat=None, timeout=60)
s.connect("tcp://127.0.0.1:54322")


data_path = "/home/linxh/data/BeautyPredict/samples/image/test7.jpg"

data = open(data_path, "rb").read()

print(s.nsfw_predict(data))

