from tensorflow.python.tools import optimize_for_inference_lib
import sys
import tensorflow as tf

def optimze_pb(graph_pb, output_path):
    with tf.gfile.GFile(graph_pb, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        with tf.Session(graph=tf.Graph()) as sess:
            graph_def = tf.graph_util.convert_variables_to_constants(sess, graph_def, ['dense_3/Softmax:0'])
            graph_def = optimize_for_inference_lib.optimize_for_inference(graph_def, ['input_1:0'], ['dense_3/Softmax:0'], tf.float32.as_datatype_enum)
            tf.train.write_graph(graph_def, "", output_path, as_text=False)

optimze_pb(sys.argv[1], sys.argv[2])