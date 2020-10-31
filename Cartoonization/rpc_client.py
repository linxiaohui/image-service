# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54331")

data_path = "x.jpg"
data = open(data_path, "rb").read()
img = s.cartoonization(data)
dat = img
with open("r.jpg", "wb") as fp:
        fp.write(dat)
