# -*- coding: utf-8 -*-
"""
https://stackoverflow.com/questions/57007707/failed-to-convert-tensorflow-frozen-graph-to-pbtxt-file
"""
import sys
import tensorflow as tf
from tensorflow.python.saved_model import signature_constants
from tensorflow.python.saved_model import tag_constants

def save(graph_pb, export_dir):
    builder = tf.saved_model.builder.SavedModelBuilder(export_dir)

    with tf.gfile.GFile(graph_pb, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    sigs = {}

    with tf.Session(graph=tf.Graph()) as sess:
        # INFO: name="" is important to ensure we don't get spurious prefixing
        tf.import_graph_def(graph_def, name='')
        g = tf.get_default_graph()

        # INFO: if name is added the input/output should be prefixed like:
        #       name=net => net/images:0 & net/features:0
        inp = tf.get_default_graph().get_tensor_by_name("input_1:0")
        out = tf.get_default_graph().get_tensor_by_name("dense_3/Softmax:0")

        sigs[signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY] = \
            tf.saved_model.signature_def_utils.predict_signature_def(
                {"in": inp}, {"out": out})

        builder.add_meta_graph_and_variables(sess,
                                            [tag_constants.SERVING],
                                            signature_def_map=sigs)

    builder.save(as_text=True)

save(sys.argv[1], sys.argv[2])