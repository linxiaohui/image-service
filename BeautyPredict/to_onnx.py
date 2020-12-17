import os

import keras
import onnx
import keras2onnx
from keras.models import Sequential
from keras.applications.resnet50 import ResNet50
from keras.layers import Dense

resnet_model_path = os.path.join('..', 'models', 'model-ldl-resnet.h5')
resnet50_model_path = os.path.join('..', 'models', 'resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5')

resnet = ResNet50(include_top=False, pooling='avg', weights=resnet50_model_path)
model = Sequential()
model.add(resnet)
model.add(Dense(5, activation='softmax'))
model.layers[0].trainable = False
model.load_weights(resnet_model_path)

onnx_model = keras2onnx.convert_keras(model, model.name)

onnx.save_model(onnx_model, "beauty-predict.onnx")



