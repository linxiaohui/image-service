# 简介

本项目使用[fast-neural-style](https://github.com/jcjohnson/fast-neural-style)提供的风格迁移的预训练模型，使用OpenCV的DNN模块加载预训练模型。 OpenCV不支持模型的训练，只支持模型推理；已经支持TensorFlow、Pytorch/Torch、Caffe、DarkNet等模型的读取。

# 模型地址

## 从官方地址下载的脚本
```bash
BASE_URL="https://cs.stanford.edu/people/jcjohns/fast-neural-style/models/"

mkdir -p models/instance_norm
cd models/instance_norm
curl -O "$BASE_URL/instance_norm/candy.t7"
curl -O "$BASE_URL/instance_norm/la_muse.t7"
curl -O "$BASE_URL/instance_norm/mosaic.t7"
curl -O "$BASE_URL/instance_norm/feathers.t7"
curl -O "$BASE_URL/instance_norm/the_scream.t7"
curl -O "$BASE_URL/instance_norm/udnie.t7"

mkdir -p ../eccv16
cd ../eccv16
curl -O "$BASE_URL/eccv16/the_wave.t7"
curl -O "$BASE_URL/eccv16/starry_night.t7"
curl -O "$BASE_URL/eccv16/la_muse.t7"
curl -O "$BASE_URL/eccv16/composition_vii.t7"
cd ../../
```

## 其他地址
[百度云]()
```
SHA256(models/eccv16/composition_vii.t7)= 34b66175dffa75d47300ca9f569e4da98face3bde3c23b3954ca5cb055e64904
SHA256(models/eccv16/la_muse.t7)= 4b821d3b4d70a42bb5caee82e1ae45a7e3d85f42c9256adfa5c9bb296e881115
SHA256(models/eccv16/starry_night.t7)= f80aedd413c5ba913e94d4812cbca73bd6c073f10c26e78ca58ee9ed5f34821b
SHA256(models/eccv16/the_wave.t7)= 57fb102191b19d1fea34df843fc4c290166a6a594fff2607e0b93459c473a9fb
SHA256(models/instance_norm/candy.t7)= 5bff84714d55b35a646822ab7199b6d40fa5fd60a8560f8f1709500b4cd8f1c4
SHA256(models/instance_norm/feathers.t7)= 51c0c48700579541d51bdbd0907de9767858dacf0e3e84e5c127335236f8091e
SHA256(models/instance_norm/la_muse.t7)= 6e22676a5565e30735f6b8ad062ffc2ae67ca471732213237ebfd559f12fc428
SHA256(models/instance_norm/mosaic.t7)= fbd7d882e9e02aafb57366e726762025ff6b2e12cd41abd44b874542b7693771
SHA256(models/instance_norm/the_scream.t7)= b8443f5573433f690cffafff55f441ac28a14c053179b0c33ddcf4da670f3732
SHA256(models/instance_norm/udnie.t7)= 3a3a2cf3472085f26d8e4bc26a1e6b2eb48e6dfc4df8ec9a9b1b0d4085aefa36
```

# 构建
   1. 在当前目录执行下载预训练模型的脚本，下载模型文件；至`models`文件中
   2. `docker build -t style-transfer:1.0 .`

# dockerhub
   `docker run -d -p 54330:54330 linxiaohui/style-transfer:1.0`

# 调用方式

```python
# -*- coding: utf-8 -*-
import zerorpc
s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54330")

data_path = "x.jpg"
data = open(data_path, "rb").read()
img = s.style_transfer(data, "udnie")
dat = img
with open("r.jpg", "wb") as fp:
    fp.write(dat)
```

# 相关项目
[DeepStyle](../DeepStyle) Another深度学习实现图片风格迁移
