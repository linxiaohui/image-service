# 简介
图片卡通化，根据CVPR2020论文《Learning to Cartoonize Using White-box Cartoon Representations》实现的项目[Github主页](https://github.com/SystemErrorWang/White-box-Cartoonization/)整合，提供RPC服务接口和Web界面。


# 构建
   * `docker build -t cartoonization:1.0 .`

# dockerhub
   `docker run -d -p 54331:54331 linxiaohui/cartoonization:1.0`

# 调用方式

```python
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
```
