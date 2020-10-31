# -*- coding: utf-8 -*-


data_path = "/home/linxh/data/BeautyPredict/samples/image/test7.jpg"

data = open(data_path, "rb").read()

import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=60)
s.connect("tcp://127.0.0.1:54321")
beauty_score = s.beauty_score(data)
print(beauty_score[0])
