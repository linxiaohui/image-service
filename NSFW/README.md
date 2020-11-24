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
## 单张图片
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
   * nsfw_predict输入参数为单张图片的二进制字节流
   * 返回示例
```json
{'1606033648.7930694.jpg': 
  {'drawings': 6.171540007926524e-05, 
   'neutral': 0.0018610728438943624,
   'sexy': 0.002201835159212351, 
   'hentai': 0.0022845808416604996, 
   'porn': 0.9935908317565918}
}
```

## 批量图片
```python
# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=60)
s.connect("tcp://127.0.0.1:54322")
images = []
for i, n in enumerate(["xx.jpg", "yy.jpg"]):
    with open(n, "rb") as fp:
        images.append((i, fp.read()))
print(s.nsfw_batch_predict(images))
```
   * nsfw_batch_predict的输入参数是一个列表，其中每个元素是（图片ID，图片二进制字节流）元组
   * 返回示例
```json
{'0.jpg': 
      {'sexy': 8.011225145310163e-05, 
       'porn': 0.0015454445965588093, 
       'hentai': 0.01900765299797058,
       'drawings': 0.0221246350556612,
       'neutral': 0.9572421908378601 },
 '1.jpg': 
      {'sexy': 0.0002633665280882269, 
       'hentai': 0.0005874683265574276, 
       'porn': 0.0009180882479995489,
       'drawings': 0.016898801550269127,
       'neutral': 0.9813323020935059}
}
```


# 技术要点
   * keras 读取图片文件
   * keras 模型加载
   