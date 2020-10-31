# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54328")

data_path = "/home/linxh/x.jpg"
data = open(data_path, "rb").read()
img = s.mark_nsfw(data)
dat = img
with open("result.jpg", "wb") as fp:
        fp.write(dat)

