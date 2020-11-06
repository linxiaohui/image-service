# -*- coding: utf-8 -*-
import zerorpc

s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54327")

data_path = "/home/linxh/p.jpg"
data = open(data_path, "rb").read()
img, score = s.face_score(data)
dat = img
with open("test.jpg", "wb") as fp:
    fp.write(dat)

print(score)
