# CertPhoto
证件照换底色

# 原理
使用[U-2-Net](https://github.com/NathanUA/U-2-Net)进行抠图，将背景替换为指定的颜色

# 模型下载

## 官方地址
   * [u2net.pth (176.3 MB)](https://drive.google.com/file/d/1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ/view?usp=sharing)
   * [u2netp.pth (4.7 MB)](https://drive.google.com/file/d/1rbSTGKAE-MTxBYHd-51l2hMOQPT_7EPy/view?usp=sharing)

## 其他方式
   * [百度云](https://pan.baidu.com/s/1kfKINZ1REk4g7tCOZtTSVw) 提取码: `vxbh`

# 构建与运行

## 本地构建镜像
   1. 下载模型文件，名为`u2net.pth`，放在当前目录中
   2. `docker build -t linxiaohui/change-bgcolor:1.0 .`

## 从DockerHub下载镜像并运行
   `docker run -d -p 54326:54326 -p 65535:80 linxiaohui/change-bgcolor:1.0`
   * 其中 `54326`端口为容器中`ZeroRPC`服务的监听端口，`80`为Web界面的监听端口； 
   * 对应的`54326`和`65535`端口为映射到的本机端口
   
# 使用

## Web界面
   * 浏览器打开，地址为宿主机地址+Web界面服务映射到的本机端口； 
   * 上传图片并选择背景颜色后，进行背景转换；
   * 转换后的图片会在页面中显示；

## RPC调用
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
   * 说明： chg_bg_color 接收参数一是一个包含图片数据的列表（每个元素为一张图片的数据），或者是单张图片数据；
   参数二是需要修改为的背景色;
   返回是对应的图片换背景色后的图片数据数组；

# 技术要点
   * 根据模型获取图片的前景
   * PIL根据颜色描述获取颜色的RGB值
   * 图片通道组合
   
# 相关功能
   * [U-2-Net](../U-2-Net) 基于的前景抠图的应用
   * [FaceSketch](../FaceSketch) 使用同样的网络训练的人物脸部素描
