# 简介
图片卡通化，根据CVPR2020论文《Learning to Cartoonize Using White-box Cartoon Representations》的项目
[Github主页](https://github.com/SystemErrorWang/White-box-Cartoonization/)整合，
直接采用项目代码库中包含的预训练模型和推理代码，提供RPC服务接口和Web界面。


# 构建与运行
## 构建
   * `docker build -t linxiaohui/cartoon:1.0 .`
   模型在代码库中的`cartoon_model`目录下

## 从DockerHub下载镜像并运行
   `docker run -d -p 54331:54331 -p 65535:80 linxiaohui/cartoon:1.0`
   * 其中 `54331`端口为容器中`54331`服务的监听端口，`80`为Web界面的监听端口； 
   * 对应的`54331`和`65535`端口为映射到的本机端口

# 使用

## Web界面
   * 浏览器打开，地址为宿主机地址+Web界面服务映射到的本机端口； 
   * 上传图片后将原图片和卡通化后的图片会在页面中显示；

## RPC调用
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

# 技术要点
   * 使用OpenCV读取图片数据、调整图片大小调用TensorFlow模型，得到输出结果；
   * OpenCV输出图片

# 相关功能
  * [FaceCartoonization](../FaceCartoonization) 同作者提出的对人脸进行卡通化的模型；（初步使用没有觉得效果比该项目更好在什么地方）
