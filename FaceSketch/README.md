# FaceSketch
人物的面部素描效果

本文受[CVPy](https://mp.weixin.qq.com/s?__biz=MzU2MDAyNzk5MA==&mid=2247484622&idx=1&sn=abe91eeb7c8a0d7a9157803ee80261a9&chksm=fc0f04f7cb788de1d3d05834e3ae5dec4769af8f830b9b69abe44b9211f1fa5436f1558ded55&token=384912966&lang=zh_CN#rd)的启发； 根据文中提供的资料链接使用数据训练模型。


# 训练数据
## APDrawingDB

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

# 构建
   1. 下载模型文件，名为`sketch.pth`，放在当前目录
   2. `docker build -t face-sketch:1.0 .`

# dockerhub
   `docker run -d -p 54325:54325 linxiaohui/face-sketch:1.0`


# 调用方式
```python
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=60)
s.connect("tcp://127.0.0.1:54325")
data_path = "/home/linxh/x.jpg"

with open(data_path, "rb") as fp:
    image_data = fp.read()
    result = s.face_sketch(image_data)
    with open("r3.png", "wb") as fp2:
        fp2.write(result[0])

```
