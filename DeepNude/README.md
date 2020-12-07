# 项目地址
   * [DeepNude_NoWatermark_withModel](https://github.com/zhengyima/DeepNude_NoWatermark_withModel)
   * [deepnude_official](https://github.com/stacklikemind/deepnude_official)

# 模型地址
   * [dn.zip](http://39.105.149.229/dn.zip)
   * [Google Drive](https://drive.google.com/drive/folders/1OKuIp0nxMUucgEScTc2vESvlpKzIWav4?usp=sharing)

# 构建方式
   * 下载模型文件，将`*.lib`放在`checkpoints`目录下
   * `docker build -t deep-nude:1.0 .`

# 启动命令
   `docker run -d -p 54328:54328 -p 65535:80 deep-nude:1.0`
   * 其中 `54328`端口为容器中RPC服务的监听端口，`80`为Web界面的监听端口；
   * 对应的`54328`和`65535`端口为映射到的本机端口.

# 调用方式
## Web界面
   * 浏览器打开，地址为宿主机地址+Web界面服务映射到的本机端口；
   * 上传图片或输入图片的URL，点击提交
   * 输入图片和模型生成的图片将同时显示对比效果

## RPC服务
```python
# -*- coding: utf-8 -*-
import zerorpc

s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54328")

data_path = "1.jpg"
data = open(data_path, "rb").read()
img = s.strip(data)
dat = img
with open("test.jpg", "wb") as fp:
    fp.write(dat)
```

# 技术要点
   * 图片水印的方式


