# -*- coding:utf-8 -*-
"""
修改自https://github.com/1093842024/anti-deepnude/blob/master/anti-deepnude.py
根据预训练模型识别NSFW图片
"""
import io
import os
import imghdr

import cv2
import keras
import numpy as np
import zerorpc
import tensorflow as tf
from tensorflow.python.platform import gfile
from PIL import Image, ImageDraw

def load_imgpil(imgpil, image_size):
    load_images = []
    image = imgpil.resize(image_size)
    image = keras.preprocessing.image.img_to_array(image)
    image /= 255
    load_images.append(image)
    return np.asarray(load_images)


class NSFWScorer(object):
    def __init__(self, mobile=False, USE_GPU=False):
        pb_file_path = os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'inception_sp_0.9924_0.09.pb')
        if USE_GPU:
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

                self.input_img = self.sess.graph.get_tensor_by_name('input_1:0')
                if not mobile:
                    self.conv_base_output = self.sess.graph.get_tensor_by_name('mixed10/concat:0')
                    self.image_size = (299, 299)
                    self.nsfw_score_result = self.sess.graph.get_tensor_by_name('dense_3/Softmax:0')
                else:
                    self.conv_base_output = self.sess.graph.get_tensor_by_name('out_relu/Relu6:0')
                    self.image_size = (224, 224)
                print(self.input_img.shape, self.conv_base_output.shape)

    def classify(self, loaded_images, with_hp=False):
        if not with_hp:
            _score = self.sess.run(self.nsfw_score_result, feed_dict= {self.input_img: loaded_images})
            print("NSFW SCORE:", _score)
            return _score
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
        if with_hp:
            ret, heatmaps = self.classify(loaded_image, True)
            heatmaps = cv2.resize(heatmaps, (w, h), interpolation=cv2.INTER_CUBIC)
            return ret, heatmaps
        ret = self.classify(loaded_image)
        return ret

MASKER = NSFWScorer()

def nsfw_score(image_data):
    ext = imghdr.what(None, image_data)
    img = Image.open(io.BytesIO(image_data)).convert('RGB')
    _score = MASKER.classify_imgpil(img, False)
    print(type(_score), _score)
    print(np.sum(_score))
    return _score[0][0]

class NSFWMaskerServer(object):
    def mark_nsfw(self, image_data):
        return nsfw_score(image_data)

if __name__ == "__main__":
    s = NSFWMaskerServer()
    for fn in ["1.jpg", "2.jpg", "3.jpg"]:
        print(fn)
        with open(fn, "rb") as fp:
            s.mark_nsfw(fp.read())

