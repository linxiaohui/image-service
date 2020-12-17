import onnx
import os
from onnx.tools import update_model_dims

onnx_model = onnx.load("beauty-predict.onnx")
# Preprocessing: get the path to the saved model
new_model_path = "beauty-predict-fix.onnx"
# Save the ONNX model
variable_length_model = update_model_dims.update_inputs_outputs_dims(onnx_model, {'resnet50_input': [1, 224, 224, 3]}, {'dense_1': [1, 5]})
onnx.save(variable_length_model, new_model_path)

~                                                      
