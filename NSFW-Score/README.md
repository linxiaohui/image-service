# 简介
[项目的github地址](https://github.com/1093842024/anti-deepnude)


# 模型下载
## 官方地址

## 其它下载方式
考虑到代码库的空间，本代码库中没有包含预训练模型。可从官方代码库中下载，或下面的地址
[百度云]()
**SHA256**：SHA256(inception_sp_0.9924_0.09.pb)= 008dc775c920bafc18e7ed68a9a2489c695aff547da3dca74b4034b0b30af0dc

# 构建与运行
## 构建
   1. 下载模型文件，名为`inception_sp_0.9924_0.09.pb`，放在当前目录下
   2. `docker build -t nsfw-score:1.0 .`

## 从DockerHub下载镜像并运行
   `docker run -d -p 54336:54336 -p 65535:80 linxiaohui/nsfw-score:1.0`
   * 其中 `54336`端口为容器中RPC服务的监听端口，`80`为Web界面的监听端口；
   * 对应的`54336`和`65535`端口为映射到的本机端口.

# 调用方式
## Web界面
   * 浏览器打开，地址为宿主机地址+Web界面服务映射到的本机端口；
   * 上传图片或输入图片的URL， 点击提交；
   * 提交后原图片和打码后的图片会在页面中同时显示，以供对比；

## RPC服务
```python
# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54336")

data_path = "x.jpg"
data = open(data_path, "rb").read()
score = s.mark_nsfw(data)
print(score)
```

# 技术要点
   * 使用`tensorboard`查看`pb`格式文件保存的模型的结构
   * 查看`pb`格式文件保存的模型各层Tensor名称

# 声明
所有权利归原作者所有。

# 相关项目
   * [Mosaic](../Mosaic) 提供了OpenCV实现对图片指定区域进行马赛克化的方式
   * [NSFW-Mask](../NSFW-Mask) 基于同样的模型（的之前的层）实现去NSFW区域进行马赛克化

