import onnx
import sys
onnx_model = onnx.load(sys.argv[1])
passes = ["extract_constant_to_initializer", "eliminate_unused_initializer"]
from onnx import optimizer
optimized_model = optimizer.optimize(onnx_model, passes)
onnx.save(optimized_model, sys.argv[2])

