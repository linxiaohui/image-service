# FaceCartoonization

面部图片卡通化， [Githu主页](https://github.com/SystemErrorWang/FacialCartoonization)

# 构建
   * `docker build -t face-cartoon:1.0 .`

# dockerhub
   * `docker run -d -p 54325:54325 linxiaohui/face-cartoon:1.0`


# 调用方式
```python
# -*- coding: utf-8 -*-
import zerorpc

s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54329")

data_path = "/home/linxh/z.jpg"
data = open(data_path, "rb").read()
img = s.cartoonize(data)
dat = img
with open("test.jpg", "wb") as fp:
    fp.write(dat)
```
