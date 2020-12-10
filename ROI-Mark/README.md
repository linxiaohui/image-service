# 简介
本项目参考[DeepMosaics](https://github.com/HypoX64/DeepMosaics)，根据其提供的预训练模型，在获取“打码”（原项目）区域后，使用OpenCV画出其区域。

# 模型下载
## 官方仓库提供的地址
   * [Google Drive](https://drive.google.com/open?id=1LTERcN33McoiztYEwBxMuRjjgxh4DEPs)
   * [百度云](https://pan.baidu.com/s/10rN3U3zd5TmfGpO_PEShqQ) `1x0a`

```
SHA256(add_face.pth)= 65586df107c2e0db5d07b1cb8d0948c5111f2766e5fb8b82c5b37a4eafb54847
SHA256(add_youknow.pth)= bd6431edaf2157a0d30c00e1b8692c28b2b606a5d05ded23d1de093d36156a69
```

# 构建与运行
## 构建
   1. 下载模型文件`add_face.pth`和`add_youknow.pth`，放在`pretrained_models`目录
   2. `docker build -t linxiaohui/roi-mark:1.0 .`

## 从DockerHub下载镜像并运行
   `docker run -d -p 54334:54334 -p 65535:80 linxiaohui/roi-mark:1.0`
   * 其中 `54334`端口为容器中RPC服务的监听端口，`80`为Web界面的监听端口；
   * 对应的`54334`和`65535`端口为映射到的本机端口.

# 调用方式

## Web界面
   * 浏览器打开，地址为宿主机地址+Web界面服务映射到的本机端口；
   * 上传图片或输入图片的URL，选择ROI区域的类型（F对应模型add_face，X对应模型add_youknow）；
   * 提交后原图片和标记了ROI区域的图片会在页面中同时显示，以供对比；

## RPC服务
```python
# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54334")

data_path = "x.jpg"
data = open(data_path, "rb").read()
img = s.mark_nsfw(data)
dat = img
with open("result.jpg", "wb") as fp:
    fp.write(dat)
```

# 技术要点
   * OpenCV 定位和描绘轮廓

# 声明
源项目采用[GPL-3.0 License](https://github.com/HypoX64/DeepMosaics/blob/master/LICENSE)；
本项目中使用的源项目中的资源所有权利归原作者所有。


# 相关项目
   * [DeepMosaic](../DeepMosaic) 同样的模型实现对ROI区域进行打码
   * [FaceDetect](../FaceDetect) OpenCV人脸检测
   * [BeautyPredict](../BeautyPredict) dlib人脸检测
   * [FaceNet](../FaceNet) 人脸检测和人脸识别


