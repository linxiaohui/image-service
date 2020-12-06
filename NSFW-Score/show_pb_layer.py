# -*- coding:utf-8 -*-
import os
import sys

import tensorflow as tf
from tensorflow.python.platform import gfile

def show_layernames(pb_file_path):
    """get all layers name"""
    sess = tf.Session()
    with gfile.FastGFile(pb_file_path, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        sess.graph.as_default()
        tf.import_graph_def(graph_def, name='')
        tensor_name_list = [tensor.name for tensor in tf.get_default_graph().as_graph_def().node]
        for tensor_name in tensor_name_list:
            print(tensor_name)

show_layernames(sys.argv[1])

