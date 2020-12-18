# -*- coding: utf-8 -*-
"""
实现预训练模型由checkpoints到pb的转换
转为pb模型后，可以使用tf2onnx转为ONNX格式（详见 https://5190m.top/2020/12/16/2020-12-16-tensorflow-pb-to-onnx/）
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import sys

import tensorflow as tf

import network
import guided_filter

def checkpoints_to_pb():
    input_photo = tf.placeholder(tf.float32, [1, None, None, 3])
    network_out = network.unet_generator(input_photo)
    final_out = guided_filter.guided_filter(input_photo, network_out, r=1, eps=5e-3)

    all_vars = tf.trainable_variables()
    gene_vars = [var for var in all_vars if 'generator' in var.name]
    saver = tf.train.Saver(var_list=gene_vars)

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)

    sess.run(tf.global_variables_initializer())
    saver.restore(sess, tf.train.latest_checkpoint(sys.argv[1]))
    print(input_photo.name, final_out.name)
    saver2 = tf.train.Saver()
    saver2.save(sess, "resave.chpt")
    for variable_name in tf.global_variables():
        print(variable_name)
    # Freeze the graph
    frozen_graph_def = tf.graph_util.convert_variables_to_constants(
        sess,
        sess.graph_def,
        ["add_1"])

    # Save the frozen graph
    with open(sys.argv[2], 'wb') as f:
        f.write(frozen_graph_def.SerializeToString())
    print("end")

checkpoints_to_pb()

