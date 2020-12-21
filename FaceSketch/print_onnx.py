import sys
import onnx
model = onnx.load(sys.argv[1])

print(onnx.checker.check_model(model))
print(onnx.helper.printable_graph(model.graph))

