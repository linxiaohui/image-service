import cv2

model_base_dir = "./models/instance_norm/"
d_model_map = {
    1: "udnie",
    2: "la_muse",
    3: "the_scream",
    4: "candy",
    5: "mosaic",
    6: "feathers",
    7: "starry_night"
}

def get_model_from_style(style: int):
    """
    加载指定风格的模型
    :param style: 模型编码
    :return: model
    """
    model_name = d_model_map.get(style, "mosaic")
    model_path = model_base_dir + model_name + ".t7"
    print(model_path)
    model = cv2.dnn.readNetFromTorch(model_path)
    return model

net = get_model_from_style(3)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

img = cv2.imread("x.jpg")

print("model read")

(h, w) = img.shape[:2]
blob = cv2.dnn.blobFromImage(img, 1.0, (w, h), (103.939, 116.779, 123.680), swapRB=False, crop=False)

print("blob")

net.setInput(blob)

print("net input")

output = net.forward()

print("forward")

# reshape输出结果, 将减去的平均值加回来，并交换各颜色通道
output = output.reshape((3, output.shape[2], output.shape[3]))
output[0] += 103.939
output[1] += 116.779
output[2] += 123.680
output = output.transpose(1, 2, 0)

cv2.imwrite("result.jpg", output)

