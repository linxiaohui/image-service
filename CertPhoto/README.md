# CertPhoto
证件照换底色

# 原理
使用`U-2-Net`进行抠图，将背景替换为指定的颜色


# 调用
```python
# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54326")

data_path = "p.jpg"
data = open(data_path, "rb").read()
img = s.chg_bg_color([data], bg_color='red')
dat = img[0]
with open("test.png", "wb") as fp:
    fp.write(dat)
```