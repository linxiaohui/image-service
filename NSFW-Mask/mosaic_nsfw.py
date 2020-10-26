# -*- coding:utf-8 -*-
"""
修改自https://github.com/1093842024/anti-deepnude/anti-deepnude.py
根据预训练模型识别NSFW图片中的区域，并对其马赛克
"""
import io
import os
import sys
import time
import shutil
import imghdr

import cv2
import keras
import numpy as np
import zerorpc
import tensorflow as tf
from tensorflow.python.platform import gfile
from PIL import Image, ImageDraw

import bbox_blur as bbox_util


def load_imgpil(imgpil, image_size):
    load_images = []
    image = imgpil.resize(image_size)
    image = keras.preprocessing.image.img_to_array(image)
    image /= 255
    load_images.append(image)
    return np.asarray(load_images)


class NSFWMasker(object):
    def __init__(self, mobile=False, USE_GPU=False):
        pb_file_path = 'model/inception_sp_0.9924_0.09_partialmodel.pb'
        if USE_GPU == True:
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"
            config = tf.ConfigProto(allow_soft_placement=True)
            config.gpu_options.allow_growth = True
        else:
            os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
            config = tf.ConfigProto(allow_soft_placement=True)

        g = tf.Graph()
        self.sess = tf.Session(graph=g, config=config)
        with self.sess.as_default():
            with self.sess.graph.as_default():
                with gfile.FastGFile(pb_file_path, 'rb') as f:
                    graph_def = tf.GraphDef()
                    graph_def.ParseFromString(f.read())
                    self.sess.graph.as_default()
                    tf.import_graph_def(graph_def, name='')
                self.sess.run(tf.global_variables_initializer())

                self.input_img = self.sess.graph.get_tensor_by_name(
                    'input_1:0')
                if mobile == False:
                    self.conv_base_output = self.sess.graph.get_tensor_by_name(
                        'mixed10/concat:0')
                    self.image_size = (299, 299)
                else:
                    self.conv_base_output = self.sess.graph.get_tensor_by_name(
                        'out_relu/Relu6:0')
                    self.image_size = (224, 224)
                print(self.input_img.shape, self.conv_base_output.shape)

    def classify(self, loaded_images, with_hp=False):
        if with_hp == False:
            raise('partial model does not support predict')
        else:
            heatmaps = self.sess.run(self.conv_base_output, feed_dict={
                                     self.input_img: loaded_images})
            if self.image_size == (299, 299):
                heatmaps_avg = np.mean(heatmaps, axis=3).reshape((8, 8))
            else:
                heatmaps_avg = np.mean(heatmaps, axis=3).reshape((7, 7))

            return [], heatmaps_avg

    def classify_imgpil(self, imgpil, with_hp=False):
        w, h = imgpil.size
        loaded_image = load_imgpil(imgpil, self.image_size)
        if with_hp == True:
            ret, heatmaps = self.classify(loaded_image, True)
            heatmaps = cv2.resize(
                heatmaps, (w, h), interpolation=cv2.INTER_CUBIC)
            return ret, heatmaps
        ret, _ = self.classify(loaded_image)
        return ret, _

    def general_mosaic(self, imgpil, weight1=1.0, weight2=0):
        ret, hp = self.classify_imgpil(imgpil, True)
        bbox, heatmaps_index, max_value, avg_value = bbox_util.analyze_box(
            hp, weight1, weight2)
        imgblur = bbox_util.img_blur_2(imgpil, hp, heatmaps_index, max_value)
        return imgblur


MASKER = NSFWMasker()


def nsfw_mosaic_region(image_data):
    ext = imghdr.what(None, image_data[:30])
    fn = f"{time.time()}.{ext}"
    with open(fn, "wb") as fp:
        fp.write(image_data)
    img = Image.open(fn).convert('RGB')
    ret, hp = MASKER.classify_imgpil(img, True)
    imgblur_general = MASKER.general_mosaic(img)
    b = io.BytesIO()
    imgblur_general.save(b, ext)
    data = b.getvalue()
    try:
        os.remove(fn)
    except:
        pass
    return data

class NSFWMaskerServer(object):
    def mark_nsfw(self, image_data):
        return nsfw_mosaic_region(image_data)

if __name__ == "__main__":
    s = zerorpc.Server(NSFWMaskerServer())
    s.bind("tcp://0.0.0.0:54328")
    s.run()
