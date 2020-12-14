# -*- coding: utf-8 -*-
"""参考 facenet项目中的 https://github.com/davidsandberg/facenet/blob/master/src/compare.py """
import io
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import imghdr

import tensorflow as tf
import numpy as np
from scipy import misc
import zerorpc
import cv2

import align.detect_face

class FaceNetOp(object):
    """"""
    def __init__(self, model_path=os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', '20180408-102900'), image_size=160, margin=44, gpu_memory_fraction=1.0):
        """
        gpu_memory_fraction: Upper bound on the amount of GPU memory that will be used by the process.
        """
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
        align_graph = tf.Graph()
        self.align_sess = tf.Session(graph=align_graph,
                                     config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
        with self.align_sess.as_default():
            with self.align_sess.graph.as_default():
                self.pnet, self.rnet, self.onet = align.detect_face.create_mtcnn(self.align_sess, None)
                print("align model LOADED!")

    def mark_faces(self, image_data, image_size=160, margin=44):
        """在图片数据上标记人脸, 返回标记后的图片数据"""
        ext = imghdr.what(None, image_data)
        minsize = 20  # minimum size of face
        threshold = [0.6, 0.7, 0.7]  # three steps's threshold
        factor = 0.709  # scale factor
        img = misc.imread(io.BytesIO(image_data), mode='RGB')
        img_size = np.asarray(img.shape)[0:2]
        bounding_boxes, _ = align.detect_face.detect_face(img, minsize, self.pnet, self.rnet, self.onet,
                                                          threshold, factor)
        for face_box in bounding_boxes:
            subfaceRec = face_box.astype(int)
            cv2.rectangle(img, (subfaceRec[0], subfaceRec[1]), (subfaceRec[2], subfaceRec[3]), (0, 255, 0), 2)
        # OpenCV BGR
        img = img[:, :, ::-1]
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        is_success, im_buf_arr = cv2.imencode("." + ext, img)
        byte_im = im_buf_arr.tobytes()
        return byte_im

if __name__ == "__main__":
    s = zerorpc.Server(FaceNetOp())
    s.bind("tcp://0.0.0.0:54335")
    s.run()
