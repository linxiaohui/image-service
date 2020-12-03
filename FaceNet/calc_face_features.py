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

import facenet
import align.detect_face

class FaceNet(object):
    """"""
    def __init__(self, model_path="/models/20180408-102900/", image_size=160, margin=44, gpu_memory_fraction=1.0):
        """
        gpu_memory_fraction: Upper bound on the amount of GPU memory that will be used by the process.
        """
        config = tf.ConfigProto(allow_soft_placement=True)
        self.g = tf.Graph()
        self.sess = tf.Session(graph=self.g, config=config)
        with self.sess.as_default():
            with self.sess.graph.as_default():
                # Load the model
                facenet.load_model(model_path)
                print("FaceNet pretrained model LOADED!")

        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
        align_graph = tf.Graph()
        self.align_sess = tf.Session(graph=align_graph,
                                     config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
        with self.align_sess.as_default():
            with self.align_sess.graph.as_default():
                self.pnet, self.rnet, self.onet = align.detect_face.create_mtcnn(self.align_sess, None)
                print("align model LOADED!")

    def load_and_align_data(self, image_data_with_id, image_size=160, margin=44):
        """
        image_size: Image size (height, width) in pixels.
        margin: Margin for the crop around the bounding box (height, width) in pixels.
        """
        minsize = 20  # minimum size of face
        threshold = [0.6, 0.7, 0.7]  # three steps's threshold
        factor = 0.709  # scale factor
        img_list = []
        for image_id, image_data in image_data_with_id:
            img = misc.imread(io.BytesIO(image_data), mode='RGB')
            img_size = np.asarray(img.shape)[0:2]
            bounding_boxes, _ = align.detect_face.detect_face(img, minsize, self.pnet, self.rnet, self.onet,
                                                              threshold, factor)
            if len(bounding_boxes) < 1:
                print("can't detect face, remove ", image_id)
                continue
            det = np.squeeze(bounding_boxes[0, 0:4])
            bb = np.zeros(4, dtype=np.int32)
            bb[0] = np.maximum(det[0] - margin / 2, 0)
            bb[1] = np.maximum(det[1] - margin / 2, 0)
            bb[2] = np.minimum(det[2] + margin / 2, img_size[1])
            bb[3] = np.minimum(det[3] + margin / 2, img_size[0])
            cropped = img[bb[1]:bb[3], bb[0]:bb[2], :]
            aligned = misc.imresize(cropped, (image_size, image_size), interp='bilinear')
            prewhitened = facenet.prewhiten(aligned)
            img_list.append((image_id, prewhitened))
        return img_list

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

    def face_feature(self, image_files, image_size=160, margin=44, gpu_memory_fraction=1.0):
        """
        image_size: Image size (height, width) in pixels.
        margin: Margin for the crop around the bounding box (height, width) in pixels.
        gpu_memory_fraction: Upper bound on the amount of GPU memory that will be used by the process.
        """
        img_list = self.load_and_align_data(image_files, image_size, margin)
        if len(img_list)==0:
            return []
        img_id, img_data = zip(*img_list)
        images = np.stack(img_data)
        images_placeholder = self.g.get_tensor_by_name("input:0")
        embeddings = self.g.get_tensor_by_name("embeddings:0")
        phase_train_placeholder = self.g.get_tensor_by_name("phase_train:0")
        # Run forward pass to calculate embeddings
        feed_dict = {images_placeholder: images,
                     phase_train_placeholder: False}
        emb = self.sess.run(embeddings, feed_dict=feed_dict)
        # print(emb.shape, emb.dtype)
        # print(emb[0, :].shape)
        ret = []
        for i, image_id in enumerate(img_id):
            ret.append((image_id, emb[i, :].tobytes()))
        return ret

if __name__ == "__main__":
    s = zerorpc.Server(FaceNet("/models/20180408-102900/"))
    s.bind("tcp://0.0.0.0:54335")
    s.run()
