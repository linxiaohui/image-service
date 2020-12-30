# -*- coding: utf-8 -*-
"""
基于[U-2-Net项目](https://github.com/NathanUA/U-2-Net)项目
将预训练模型转换为ONNX格式, 使用ONNX进行推理，分离前景图片和背景图片
"""
import io
import imghdr

import skimage.io
import skimage.transform
import zerorpc
import onnxruntime
import numpy as np
from PIL import Image
from PIL import ImageOps

# normalize the predicted SOD probability map
def norm_pred(d):
    ma = np.max(d)
    mi = np.min(d)
    dn = (d-mi)/(ma-mi)
    return dn


class U2NetONNX(object):
    def __init__(self, onnx_path="u2net.onnx"):
        self.onnx_session = onnxruntime.InferenceSession(onnx_path)
        self.input_name = [node.name for node in self.onnx_session.get_inputs()]
        self.output_name = [node.name for node in self.onnx_session.get_outputs()]
        print("input_name:{}".format(self.input_name))
        print("output_name:{}".format(self.output_name))

    def forward(self, image_numpy):
        # 输入数据的类型必须与模型一致
        input_feed = {}
        for name in self.input_name:
            input_feed[name] = image_numpy
        out = self.onnx_session.run(self.output_name, input_feed=input_feed)
        return out

    @staticmethod
    def gen_output(image_data, predict):
        ori_image = skimage.io.imread(io.BytesIO(image_data))
        # 前景图
        fg_img = np.zeros((ori_image.shape[0], ori_image.shape[1], 4), dtype=np.uint8)
        # 背景图
        bg_img = np.zeros((ori_image.shape[0], ori_image.shape[1], 4), dtype=np.uint8)
        # 生成Mask并调整至原始图片大小
        pred_np = predict.squeeze()
        im = Image.fromarray(pred_np*255).convert('RGB')
        imo = im.resize((ori_image.shape[1], ori_image.shape[0]), resample=Image.BILINEAR)
        mask = np.asarray(imo)
        # 抠出前景图片
        fg_img[:, :, 0] = ori_image[:, :, 0]
        fg_img[:, :, 1] = ori_image[:, :, 1]
        fg_img[:, :, 2] = ori_image[:, :, 2]
        fg_img[:, :, 3] = mask[:, :, 0]
        # 抠出背景图片
        bg_img[:, :, 0] = ori_image[:, :, 0]
        bg_img[:, :, 1] = ori_image[:, :, 1]
        bg_img[:, :, 2] = ori_image[:, :, 2]
        bg_mask = np.asarray(ImageOps.invert(imo))
        bg_img[:, :, 3] = bg_mask[:, :, 0]
        fg_im = Image.fromarray(np.uint8(fg_img)).convert("RGBA")
        fg_io = io.BytesIO()
        fg_im.save(fg_io, "png")
        fg_data = fg_io.getvalue()
        bg_im = Image.fromarray(np.uint8(bg_img)).convert("RGBA")
        bg_io = io.BytesIO()
        bg_im.save(bg_io, "png")
        bg_data = bg_io.getvalue()
        return fg_data, bg_data

    def seperate_image(self, image_data):
        """
        对输入的图片数据进行预处理，调用ONNX推理函数，生成Mask
        并根据Mask，将输入图片分离为前景图和背景图
        """
        image_bytes = io.BytesIO(image_data)
        image = skimage.io.imread(image_bytes)
        image = skimage.transform.resize(image, (320, 320), mode='constant')
        input_img = np.zeros((image.shape[0], image.shape[1], 3))
        image = image / np.max(image)
        input_img[:, :, 0] = (image[:, :, 0] - 0.485) / 0.229
        input_img[:, :, 1] = (image[:, :, 1] - 0.456) / 0.224
        input_img[:, :, 2] = (image[:, :, 2] - 0.406) / 0.225
        input_img = input_img.transpose((2, 0, 1))
        input_img = input_img[np.newaxis, :, :, :]
        # fix onnxruntime.capi.onnxruntime_pybind11_state.InvalidArgument:
        # [ONNXRuntimeError] : 2 : INVALID_ARGUMENT : Unexpected input data type.
        # Actual: (N11onnxruntime17PrimitiveDataTypeIdEE) , expected: (N11onnxruntime17PrimitiveDataTypeIfEE)
        input_img = input_img.astype(np.float32)
        output, *_ = self.forward(input_img)
        output = output[:, 0, :, :]
        pred = norm_pred(output)
        fg_data, bg_data = self.gen_output(image_data, pred)
        return fg_data, bg_data

if __name__ == "__main__":
    with open("x.jpg", "rb") as fp:
        dat = fp.read()
    s = U2NetONNX()
    f, b = s.seperate_image(dat)
    with open("f.png", "wb") as fp:
        fp.write(f)
    with open("g.png", "wb") as fp:
        fp.write(b)
    s = zerorpc.Server(U2NetONNX())
    s.bind("tcp://0.0.0.0:54331")
    s.run()


