# 主页
   基于深度学习的AI颜值评分模型。[项目的github地址](https://github.com/ustcqidi/BeautyPredict)

# 模型下载

## 官方地址
   [Label distribution learning model](https://pan.baidu.com/s/1d6jBWNxy3eXS5tz3TvCwsw)

```
SHA256(model-ldl-resnet.h5)= c860946edbd58401dc6b5cea94b2e3c7246b4be08ce59e0eb7165ec25df8a436
SHA256(resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5)= 751baea102ae63f0990607883ff819cfe18276d5116605673c5ff7e42e34e945
```

# 版本事项
确定预训练模型的版本的方式
```python
import h5py
f=h5py.File("models/model-ldl-resnet.h5", "r")
f.attrs['keras_version']
```
输出`b'2.0.5'`
   **需要注意的是h5py的版本** 这里是 2.10.0

# 构建与运行
## 构建
   1. 下载模型文件，名为`resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5`，放在当前目录
   2. 下载模型文件，名为`model-ldl-resnet.h5`，放在`models`目录下
   3. `docker build -t linxiaohui/beauty-predit:1.0 .`

## 从DockerHub下载镜像并运行
   `docker run -d -p 54321:54321 -p 65535:80 linxiaohui/beauty-predit:1.0`
   * 其中 `54321`端口为容器中RPC服务的监听端口，`80`为Web界面的监听端口；
   * 对应的`54321`和`65535`端口为映射到的本机端口.

# 调用方式
## Web界面
   * 浏览器打开，地址为宿主机地址+Web界面服务映射到的本机端口；
   * 上传图片或输入图片的URL，点击提交
   * 提交后，输入图片以及其“颜值”会显示在页面中，以供评估效果；

## RPC服务
```python
# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=60)
s.connect("tcp://127.0.0.1:54321")
data_path = "test.jpg"
data = open(data_path, "rb").read()
beauty_score = s.beauty_score(data)
print(beauty_score[0])
```
   * 说明： beauty_score返回时一个数组，为其中每一张脸的评分

# 技术要点
使用dlib的人脸检测功能，确定人脸的区域，使用OpenCV调整人脸区域的大小后调用模型，得到评分;
在图片上标注人脸的区域以及其评分

# 相关功能
   * [FaceRank](../FaceRank) 使用“公式”计算颜值，其中有使用dlib进行人脸关键点检测
   * [FaceDetect](../FaceDetect)  使用OpenCV进行人脸的检测
