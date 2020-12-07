# FaceCartoonization

面部图片卡通化， [Githu主页](https://github.com/SystemErrorWang/FacialCartoonization)

# 构建与运行
# 本地构建
   * `docker build -t linxiaohui/face-cartoon:1.0 .`

# 从dockerhub拉取并运行
   `docker run -d -p 54329:54329 -p 65535:80 linxiaohui/face-cartoon:1.0`
   * 其中 `54329`端口为容器中RPC服务的监听端口，`80`为Web界面的监听端口；
   * 对应的`54329`和`65535`端口为映射到的本机端口.


# 调用方式
```python
# -*- coding: utf-8 -*-
import zerorpc

s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54329")

data_path = "z.jpg"
data = open(data_path, "rb").read()
img = s.cartoonize(data)
dat = img
with open("test.jpg", "wb") as fp:
    fp.write(dat)
```

# 相关应用
   * [Cartoonization](../Cartoonization)  同作者提出的对图片进行卡通化处理的模型;