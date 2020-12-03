# FaceNet
使用深度学习模型进行人脸的检测和特征提取，进而可以进行人脸识别。 [项目地址](https://github.com/davidsandberg/facenet)

在实际使用发现，其人脸检测的效果比OpenCV及dlib要好（如，可以识别图片中倾斜的人脸）。

# 模型下载

## 官方地址
   * [20180408-102900](https://drive.google.com/open?id=1R77HmFADxe87GmoLwzfgMu_HY0IhcyBz)
   
# 构建与运行
## 构建
   * 下载预训练模型，将文件夹`20180408-102900` 放在当前目录
   * `docker build -t linxiaohui/face-net:1.0 .`

## 从DockerHub下载镜像并运行
   `docker run -d -p 54335:54335 -p 65535:80 linxiaohui/face-net:1.0`
   * 其中 `54335`端口为容器中RPC服务的监听端口，`80`为Web界面的监听端口；
   * 对应的`54335`和`65535`端口为映射到的本机端口.

# 调用方式
## Web界面
   * 浏览器打开，地址为宿主机地址+Web界面服务映射到的本机端口；
   * 上传图片或输入图片的URL，点击提交
   * 提交后，输入图片以及标示了面部区域的图片会显示在页面中，以供评估效果；

## RPC服务
```python
# -*- coding: utf-8 -*-
import zerorpc
import numpy as np
s = zerorpc.Client(heartbeat=None, timeout=60)
s.connect("tcp://127.0.0.1:54335")
data_path = "test.jpg"
data = open(data_path, "rb").read()
rec = [(1, data)]
ret = s.face_feature(rec)
for image_id, image_feature in ret:
    print(image_id)
    print(np.frombuffer(image_feature, dtype=np.float32))
img = s.mark_face(data)
with open("r.jpg", "wb") as fp:
    fp.write(img)
```
   * 说明： face_feature接收参数为一个元素为 (id，图片数据流)元组的列表，
   （因为内部处理逻辑会首先剔除没有人脸的图片并且不返回，所以需要标记图片的ID）； 
   返回有人脸的图片的(ID, 特征向量的二进制表示）的列表；
   
   mark_faces接收参数为图片的二进制数据，返回标记了所有人脸的图片的二进制数据；
   
# 技术要点
   * align 人脸对齐
   * FaceNet计算特征向量
   * 同一人脸的判断标准
