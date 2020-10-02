# FaceSketch
人物的面部素描效果


# 训练数据


# 关于PyTorch的使用

## CUDA_VISIBLE_DEVICES
在GPU服务器上训练模型的同时，试验模型效果的脚本报cuda Out of Memory错误；因为二者试图使用同一个显卡
`export CUDA_VISIBLE_DEVICES=1,2,3,4` 后执行即可

# 预训练模型
[百度云]()


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
