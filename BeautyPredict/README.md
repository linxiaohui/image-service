# 主页
   [项目的github地址](https://github.com/ustcqidi/BeautyPredict)

# 模型下载

## 官方地址
   [Label distribution learning model](https://pan.baidu.com/s/1d6jBWNxy3eXS5tz3TvCwsw)

## 其他方式
    [百度云]()

# 版本事项


# 构建
   1. 下载模型文件，名为`resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5`，放在当前目录
   2. 下载模型文件，名为`model-ldl-resnet.h5`，放在`models`目录下
   3. `docker build -t beauty-predit:1.0 .`

# dockerhub

   `docker run -d -p 54321:54321 linxiaohui/beauty-predit:1.0`


# 调用方式

```python
# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=60)
s.connect("tcp://127.0.0.1:54321")
data_path = "/home/linxh/data/BeautyPredict/samples/image/test7.jpg"
data = open(data_path, "rb").read()
beauty_score = z.beauty_score(data)
print(beauty_score[0])
```
