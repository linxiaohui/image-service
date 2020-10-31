# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54330")

data_path = "/home/linxh/p.jpg"
data = open(data_path, "rb").read()
img = s.style_transfer(data, "udnie")
dat = img
with open("r.jpg", "wb") as fp:
        fp.write(dat)
