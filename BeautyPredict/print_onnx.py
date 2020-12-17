import onnx
model = onnx.load("beauty-predict.onnx")

print(onnx.checker.check_model(model))
print(onnx.helper.printable_graph(model.graph))
