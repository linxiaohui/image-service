# FaceSketch
人物的面部素描效果

本文受[CVPy](https://mp.weixin.qq.com/s?__biz=MzU2MDAyNzk5MA==&mid=2247484622&idx=1&sn=abe91eeb7c8a0d7a9157803ee80261a9&chksm=fc0f04f7cb788de1d3d05834e3ae5dec4769af8f830b9b69abe44b9211f1fa5436f1558ded55&token=384912966&lang=zh_CN#rd)的启发； 根据文中提供的资料链接使用数据训练模型。


# 训练数据
[APDrawingDB](https://cg.cs.tsinghua.edu.cn/people/~Yongjin/APDrawingDB.zip)

## 训练数据处理代码
代码库中有基于`Pillow`的处理版本； 下面的代码基于`opencv`

```python
# -*- coding: utf-8 -*-
import os
import sys

import cv2 

DATA_DIR = sys.argv[1]

def split_image(fn_path):
    img = cv2.imread(fn_path)
    fn = fn_path.split(os.sep)[-1].strip(".png")
    train_fn = fn+"_train.png"
    label_fn = fn+"_label.png"
    cropped = img[0:512, 0:512] # 裁剪坐标为[y0:y1, x0:x1]
    cv2.imwrite(train_fn, cropped)
    cropped = img[0:512, 512:1024] # 裁剪坐标为[y0:y1, x0:x1]
    cv2.imwrite(label_fn, cropped)

os.chdir(DATA_DIR)
for f in os.listdir("."):
    split_image(f)
```

# 关于PyTorch的使用

## CUDA_VISIBLE_DEVICES
在GPU服务器上训练模型的同时，试验模型效果的脚本报cuda Out of Memory错误；因为二者试图使用同一个显卡
`export CUDA_VISIBLE_DEVICES=1,2,3,4` 后执行即可

# 预训练模型
[百度云](https://pan.baidu.com/s/1kFO-lrRPnb57NL-gptFwzA) 提取码: `v42s`

# 构建与运行
## 构建
   1. 下载模型文件，名为`sketch.pth`，放在当前目录
   2. `docker build -t linxiaohui/face-sketch:1.0 .`

## 从DockerHub下载镜像并运行
   `docker run -d -p 54325:54325 -p 65535:80 linxiaohui/face-sketch:1.0`
   * 其中 `54325`端口为容器中RPC服务的监听端口，`80`为Web界面的监听端口；
   * 对应的`54325`和`65535`端口为映射到的本机端口.

# 调用方式
## Web界面
   * 浏览器打开，地址为宿主机地址+Web界面服务映射到的本机端口；
   * 上传图片或输入图片的URL，点击提交
   * 提交后原图片和形成的素描图片会在页面中同时显示，以供对比模型的效果；

## RPC服务
```python
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=60)
s.connect("tcp://127.0.0.1:54325")
data_path = "x.png"

with open(data_path, "rb") as fp:
    image_data = fp.read()
    result = s.face_sketch(image_data)
    with open("r3.png", "wb") as fp2:
        fp2.write(result[0])
```
   * 说明：face_sketch输入参数为一张图片的数据，或者一个图片数组的列表; 返回为一个列表，为对应输入图片的卡通化图片数据（如果输入是一张图片，返回也是有一个元素的列表。

# 技术要点
   * 实现图片黑白互换
   * Image 与 np.array的转换


# 相关功能
   * [../U-2-Net](基础模型，进行前景扣图)
   * [../CertPhoto](基于U-2-Net的修改证件照背景图片)
