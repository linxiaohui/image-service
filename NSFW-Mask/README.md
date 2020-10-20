# 简介
[项目的github地址](https://github.com/1093842024/anti-deepnude)
该项目实现对NSFW图片的相关区域自动打码。根据测试数据，对NSFW图片，其不是打码“关键点”，是会对整个区域“打码”。

# 模型下载
## 官方地址
官方的代码仓库中包含了[预训练模型](https://github.com/1093842024/anti-deepnude/blob/master/weights/inception_sp_0.9924_0.09_partialmodel.pb). 

## 其它下载方式
考虑到代码库的空间，本代码库中没有包含预训练模型。可从官方代码库中下载，或下面的地址
[百度云]()
**SHA256**： (model/inception_sp_0.9924_0.09_partialmodel.pb)= 4a057af525b70b06b73e751e1b7d531af86e091710567a90119b671801e268e3

# 构建
   1. 下载模型文件，名为`inception_sp_0.9924_0.09_partialmodel.pb`，放在`model`目录
   2. `docker build -t nsfw-mask:1.0 .`

# dockerhub
   `docker run -d -p 54328:54328 linxiaohui/nsfw-mask:1.0`

# 调用方式
```python
# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54328")

data_path = "x.jpg"
data = open(data_path, "rb").read()
img = s.mark_nsfw(data)
dat = img
with open("result.jpg", "wb") as fp:
    fp.write(dat)
```

# 声明
所有权利归原作者所有。

# 相关项目
[Mosaic](../Mosaic) 提供了OpenCV实现对图片指定区域进行马赛克化的方式

