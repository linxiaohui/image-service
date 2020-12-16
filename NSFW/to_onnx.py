import keras
import onnx
import keras2onnx

model =  keras.models.load_model("nsfw.299x299.h5")
onnx_model = keras2onnx.convert_keras(model, model.name)

onnx.save_model(onnx_model, "nsfw.onnx")

