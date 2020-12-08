# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54336")

data_path = "/home/linxh/x.jpg"
data = open(data_path, "rb").read()
img = s.mark_nsfw(data)
print(img)


