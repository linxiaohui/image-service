# 主页
   [项目的github地址](https://github.com/GantMan/nsfw_model)

# 模型下载

## 官方地址
   [Keras 299x299 Image Model](https://s3.amazonaws.com/nsfwdetector/nsfw.299x299.h5)
   
## 其他方式
   [百度云](https://pan.baidu.com/s/15R-M4JdnjjhY04JgoVDYnw) 提取码: `uhkq`

```
SHA256(nsfw.299x299.h5)= b27797fd59c5d2c1fc21d8d6cf886eae4ee3b834f9fd7a4bd85c73d17362c26c
```

# 版本事项
确定预训练模型的版本的方式
```python
import h5py
f=h5py.File("nsfw.299x299.h5", "r")
f.attrs['keras_version']
```
输出`b'2.2.4'`

# 构建与运行

## 本地构建镜像
   1. 下载模型文件，名为`nsfw.299x299.h5`，放在当前目录
   2. `docker build -t linxiaohui/nsfw-service:1.0 .`

## 从DockerHub下载镜像并运行
   `docker run -d -p 54322:54322 linxiaohui/nsfw-service:1.0`
   * 其中 `54322`端口为容器中`ZeroRPC`服务的监听端口，映射到本机的 `54322`端口

# 调用方式
```python
# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=60)
s.connect("tcp://127.0.0.1:54322")
data_path = "test7.jpg"
with open(data_path, "rb") as fp:
    data = fp.read()
print(s.nsfw_predict(data))
```
   * nsfw_predict输入参数为图片的数据
   * 返回示例
```
{'1606033648.7930694.jpg': {'drawings': 6.171540007926524e-05, 'neutral': 0.0018610728438943624, 'sexy': 0.002201835159212351, 'hentai': 0.0022845808416604996, 'porn': 0.9935908317565918}}
```
