# 简介
   AI抠图，[项目的github地址](https://github.com/NathanUA/U-2-Net)

# 模型下载

## 官方地址
   * [u2net.pth (176.3 MB)](https://drive.google.com/file/d/1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ/view?usp=sharing)
   * [u2netp.pth (4.7 MB)](https://drive.google.com/file/d/1rbSTGKAE-MTxBYHd-51l2hMOQPT_7EPy/view?usp=sharing)

## 其他方式
   * [百度云](https://pan.baidu.com/s/1kfKINZ1REk4g7tCOZtTSVw) 提取码: `vxbh`

```
SHA256(u2net.pth)= 10025a17f49cd3208afc342b589890e402ee63123d6f2d289a4a0903695cce58
SHA256(u2netp.pth)= e7567cde013fb64813973ce6e1ecc25a80c05c3ca7adbc5a54f3c3d90991b854
```

# 构建
   1. 下载模型文件，名为`u2net.pth`，放在`model`目录
   2. `docker build -t u2net:1.0 .`

# dockerhub
   `docker run -d -p 54323:54323 linxiaohui/u2net:1.0`

# 调用方式
```python
# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54323")

data_path = "x.png"
data = open(data_path, "rb").read()
img = s.cutout([data])
dat = img[0]
with open("test.png", "wb") as fp:
    fp.write(dat)
```
