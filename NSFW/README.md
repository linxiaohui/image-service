# 主页
   [项目的github地址](https://github.com/GantMan/nsfw_model)

# 模型下载

## 官方地址
   [Keras 299x299 Image Model](https://s3.amazonaws.com/nsfwdetector/nsfw.299x299.h5)
   
## 其他方式
   [百度云](https://pan.baidu.com/s/15R-M4JdnjjhY04JgoVDYnw) 提取码: `uhkq`

链接:  
# 构建
   1. 下载模型文件，名为`nsfw.299x299.h5`，放在当前目录
   2. `docker build -t nsfw-service:1.0 .`

# dockerhub

   `docker run -d -p 54322:54322 linxiaohui/nsfw-service:1.0`

# 调用方式

```python
# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=60)
s.connect("tcp://127.0.0.1:54322")
data_path = "/home/linxh/data/BeautyPredict/samples/image/test7.jpg"
data = open(data_path, "rb").read()
print(s.nsfw_predict(data))
```
