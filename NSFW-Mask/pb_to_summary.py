import sys
import tensorflow as tf

tf.reset_default_graph()
with open(sys.argv[1], "rb") as fp:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(fp.read())
    tf.import_graph_def(graph_def, name="")
    tf.summary.FileWriter("/tmp/graph", tf.get_default_graph())

