# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54336")

data_path = "x.jpg"
data = open(data_path, "rb").read()
score = s.score_nsfw(data)
print(score)


