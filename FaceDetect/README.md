# FaceDetect
使用OpenCV人脸检测的示例

# 构建与运行
## 构建
   * `docker build -t face-detect:1.0 .`

## 从DockerHub下载镜像并运行
   `docker run -d -p 54324:54324 -p 65535:80 linxiaohui/face-detect:1.0`
   * 其中 `54324`端口为容器中RPC服务的监听端口，`80`为Web界面的监听端口；
   * 对应的`54324`和`65535`端口为映射到的本机端口.

# 调用方式
## Web界面
   * 浏览器打开，地址为宿主机地址+Web界面服务映射到的本机端口；
   * 上传图片或输入图片的URL，点击提交
   * 提交后，输入图片以及标示了面部区域的图片会显示在页面中，以供评估效果；

## RPC服务
```python
# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=60)
s.connect("tcp://127.0.0.1:54324")
data_path = "test.jpg"
data = open(data_path, "rb").read()
img = s.face_mark(data)
with open("r.jpg", "wb") as fp:
    fp.write(img)
```

