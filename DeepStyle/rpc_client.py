# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54332")

data_path = "/home/linxh/t.jpg"
data = open(data_path, "rb").read()
img = s.style_transfer(data, "cezanne")
dat = img
with open("r.jpg", "wb") as fp:
        fp.write(dat)

