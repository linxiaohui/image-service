# -*- coding: utf-8 -*-
import pprint 

import tensorflow as tf

reader=tf.train.NewCheckpointReader("cartoon_model/model-33999")

pprint.pprint(reader.debug_string().decode("utf-8"))

pb_gfile_path = "cartoon.pb"

with tf.Session() as sess:
    for key in reader.get_variable_to_shape_map():
        tf.Variable(reader.get_tensor(key), name=key)
    #tf.global_variables_initializer()

    with tf.gfile.FastGFile(pb_gfile_path, "wb") as f:
        f.write(sess.graph_def.SerializeToString())
