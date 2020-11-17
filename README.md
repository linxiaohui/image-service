# image-service
Dockers for Image Service

# 动机
在进行与图片处理有关内容的学习和调研过程中，发现一些使用上的问题：
   1. 相关功能依赖库的版本等环境问题
   2. 预训练模型下载难的问题
   3. 接口使用方式的问题

# 目标
为解决上述问题，方便相关功能的使用，建立本项目：
   1. 收集OpenCV、dlib、深度学习 等技术进行图片处理的相关技术和方法
   2. 使用docker的方式组织
   3. 梳理预训练模型的下载方式以便于获取
   4. 示例代码描述功能以及调用、返回形式
   5. 提供Web界面以便直观展示效果

# 内容

## BeautyPredict
AI颜值评分

## Cartoonization
图片卡通化

## CertPhote
证件照换背景

## DeepMosaic
根据预训练模型对ROI区域进行打码

## DeepStyle
Another图片风格迁移

## FaceCartoonization
人脸图片卡通化

## FaceDetect
人脸识别

## FaceRank
人脸关键点识别，并根据公式计算“颜值”

## FaceSketch
人脸素描

## Mosaic
对图片中选择的区域马赛克

## NSFW
NSFW（Not Suitalbe For Work） 图片的识别

## NSFW-Mask
实现对NSFW图片进行区域打码

## ROI-Mark
根据预训练模型画出ROI区域

## StyleTransfer
使用OpenCV进行风格迁移

## U-2-Net
AI抠图


# 使用方式
   * 项目中每个子目录一个功能；
   * 子目录中包含`Dockerfile`文件，按照每个子目录的`README`进行构建和测试。

# ALL-IN-ONE Web App
   * Web应用使用了 [clearmin模版](https://github.com/paomedia/clearmin)

## Docker构建与运行
   * 在项目的根目录 `docker build -t linxiaohui/image-service:1.0` 构建包含所有功能的Web（不包含模型）
   * 或者 `docker pull linxiaohui/image-service:1.0`
   * 运行时 `docker run -d -p 65535:80 -v models_path:/models linxiaohui/image-service:1.0`

## 直接运行
   * 按Dockerfile安装合适的python包
   * bash start_standalone.bash

## Demo
`http://demo.5190m.top:65535`

# 声明
本项目仅对一些功能进行整理，并可能根据需要进行一定的适应性改动，目的是方便研究与可获取性；
本项目作者不对项目及引用的功能做任何形式的保证，对使用这些功能的结果不负任何形式的责任；
所有功能和模型所有权或著作权属于原作者。
