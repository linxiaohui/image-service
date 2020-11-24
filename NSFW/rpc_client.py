# -*- coding: utf-8 -*-

import zerorpc

s = zerorpc.Client(heartbeat=None, timeout=60)
s.connect("tcp://127.0.0.1:54322")

# 单张图片
data_path = "1.jpg"
data = open(data_path, "rb").read()
print(s.nsfw_predict(data))

# 批量调用
images = []
for i, n in enumerate(["1.jpg", "2.jpg"]):
    with open(n, "rb") as fp:
        images.append((i, fp.read()))
print(s.nsfw_batch_predict(images))



