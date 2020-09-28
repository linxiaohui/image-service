# FaceSketch
人物的面部素描效果

# 关于PyTorch的使用

## CUDA_VISIBLE_DEVICES
在GPU服务器上训练模型的同时，试验模型效果的脚本报cuda Out of Memory错误；因为二者试图使用同一个显卡
`export CUDA_VISIBLE_DEVICES=1,2,3,4` 后执行即可



