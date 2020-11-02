# 简介
本项目参考[DeepMosaics](https://github.com/HypoX64/DeepMosaics)，根据其提供的预训练模型，对图片特定的区域“打码”

# 模型下载
## 官方仓库提供的地址
   * [Google Drive](https://drive.google.com/open?id=1LTERcN33McoiztYEwBxMuRjjgxh4DEPs)
   * [百度云](https://pan.baidu.com/s/10rN3U3zd5TmfGpO_PEShqQ) `1x0a`

```
```

# 构建与运行
## 构建
   1. 下载模型文件`add_face.pth`和`add_youknow.pth`，放在`pretrained_models`目录
   2. `docker build -t deep-mosaic:1.0 .`

## 从DockerHub下载镜像并运行
   `docker run -d -p 54333:54333 -p 65535:80 linxiaohui/deep-mosaic:1.0`
   * 其中 `54333`端口为容器中RPC服务的监听端口，`80`为Web界面的监听端口；
   * 对应的`54333`和`65535`端口为映射到的本机端口.

# 调用方式

## Web界面
   * 浏览器打开，地址为宿主机地址+Web界面服务映射到的本机端口；
   * 上传图片或输入图片的URL，选择ROI区域的类型（F对应模型add_face，X对应模型add_youknow）；
   * 提交后原图片和对ROI区域打码后的图片会在页面中同时显示，以供对比模型效果；

## RPC服务
```python
# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54333")

data_path = "x.jpg"
data = open(data_path, "rb").read()
img = s.deep_mosaic(data, "face")
dat = img
with open("r.jpg", "wb") as fp:
        fp.write(dat)
```

# 声明
源项目采用[GPL-3.0 License](https://github.com/HypoX64/DeepMosaics/blob/master/LICENSE)；
本项目中使用的源项目中的资源所有权利归原作者所有。


# 相关项目
[ROI-Mark](../ROI-Mark) 利用同样的模型通过OpenCV画出ROI区域的轮廓
