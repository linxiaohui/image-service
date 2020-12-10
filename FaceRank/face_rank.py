# -*- coding: utf-8 -*-
import os
import imghdr
from math import sqrt, pow, fabs

import numpy as np
import zerorpc
import cv2
import dlib

from dlib_landmarks import *

DETECTOR = dlib.get_frontal_face_detector()
LANDMARKER = dlib.shape_predictor(os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'shape_predictor_68_face_landmarks.dat'))

class Point2D(object):
    def __init__(self):
        self.x = 0
        self.y = 0

def cacl_distance(p1, p2):
    return sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2))

def cacl_mid_point(p1, p2):
    res_mid_point = Point2D()
    res_mid_point.x = (p1.x + p2.x) / 2
    res_mid_point.y = (p1.y + p2.y) / 2
    return res_mid_point

def facial_rater(shape):
    eyebrow_mid = cacl_mid_point(shape.part(left_eyebrow_right_corner),
                                 shape.part(right_eyebrow_left_corner))
    d1 = cacl_distance(shape.part(nose_contour_lower_middle), eyebrow_mid)
    d2 = cacl_distance(shape.part(left_eye_right_corner),
                       shape.part(right_eye_left_corner))
    d3 = cacl_distance(shape.part(nose_left), shape.part(nose_right))
    d4 = cacl_distance(shape.part(contour_left1), shape.part(contour_right1))
    d5 = cacl_distance(shape.part(contour_chin),
                       shape.part(nose_contour_lower_middle))
    d6_left = cacl_distance(shape.part(left_eye_left_corner),
                            shape.part(left_eye_right_corner))
    d6_right = cacl_distance(shape.part(right_eye_left_corner),
                             shape.part(right_eye_right_corner))
    d7 = cacl_distance(shape.part(mouth_left_corner),
                       shape.part(mouth_right_corner))
    d8 = cacl_distance(shape.part(contour_left4), shape.part(contour_right4))

    init_score = 100
    deduction = 0

    # 眼角距离为脸宽的 1/5，
    deduction += fabs((d2 / d4) * 100 - 25)
    # 鼻子宽度为脸宽的 1/5
    deduction += fabs((d3 / d4) * 100 - 25)
    # 眼睛的宽度，应为同一水平脸部宽度的 1/5
    eye_dist_avg = (d6_left + d6_right) / 2
    deduction += fabs(eye_dist_avg / d4 * 100 - 25)
    # 理想嘴巴宽度应为同一脸部宽度的 1/2
    deduction += fabs((d7 / d8) * 100 - 50)
    # 下巴到鼻子下方的高度 == 眉毛中点到鼻子最低处的距离
    deduction += fabs(d5 - d1)
    final_score = init_score - deduction + 20
    return final_score

def facial_processor(img, shape, image_type='.png'):
    for i in range(68):
        cv2.circle(img, (shape.part(i).x, shape.part(i).y), 5, (0, 255, 0), -1, 8)
    is_success, im_buf_arr = cv2.imencode(image_type, img)
    byte_im = im_buf_arr.tobytes()
    return byte_im

    
def face_detector(image_data):
    """检测图片数据中的人脸，返回一个元组；
    如果找到则标记其中第一张脸的位置及评分，否则返回(原图片数据, -1)"""
    ext = imghdr.what(None, image_data)
    img = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    faces = DETECTOR(img, 1)
    if len(faces) <= 0:
        return image_data, -1
    else:
        shape = LANDMARKER(img, faces[0])
        score = facial_rater(shape)
        marked_img = facial_processor(img, shape, "."+ext)
        return marked_img, score

class FaceScorer(object):
    def face_score(self, image_data):
        return face_detector(image_data)

if __name__ == "__main__":
    s = zerorpc.Server(FaceScorer())
    s.bind("tcp://0.0.0.0:54327")
    s.run()
