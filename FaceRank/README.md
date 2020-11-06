# 主页
参考[github上的项目FaceRank](https://github.com/pwfee/FaceRank)

该项目使用dlib进行人脸检测，利用公式计算“颜值”；

# 模型文件
shape_predictor_68_face_landmarks.dat

# 构建与运行
## 构建
   1. 下载模型文件，名为`shape_predictor_68_face_landmarks.dat`，放在当前目录
   2. `docker build -t face-rank:1.0 .`

## 从DockerHub下载镜像并运行
   `docker run -d -p 54327:54327 -p 65535:80 linxiaohui/face-rank:1.0`
   * 其中 `54327`端口为容器中RPC服务的监听端口，`80`为Web界面的监听端口；
   * 对应的`54327`和`65535`端口为映射到的本机端口.

# 调用方式
## Web界面
   * 浏览器打开，地址为宿主机地址+Web界面服务映射到的本机端口；
   * 上传图片或输入图片的URL，点击提交
   * 提交后，经过标注的面部图片和根据不同方式的”颜值”会显示在页面中，以供评估效果；

## RPC服务
```python
import zerorpc

s = zerorpc.Client(heartbeat=None, timeout=180)
s.connect("tcp://127.0.0.1:54327")

data_path = "p.jpg"
data = open(data_path, "rb").read()
img, score = s.face_score(data)
dat = img
with open("test.jpg", "wb") as fp:
    fp.write(dat)

print(score)
```


# 相关
   * [FaceDetect](../FaceDetect) 使用OpenCV进行人脸的检测
   * [BeautyPredict](../BeautyPredict) 使用深度学习进行模型的“颜值评分”
   * [Baidu AIP人脸API](https://cloud.baidu.com/doc/FACE/s/ek37c1qiz)
   * [Face++ API](https://console.faceplusplus.com.cn/documents/4888373)

更多信息可以参见上述项目的主页.

