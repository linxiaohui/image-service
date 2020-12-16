import torch

from model import U2NET

MODEL_DIR = os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'sketch.pth')
NET = U2NET(3, 1)
NET.load_state_dict(torch.load(MODEL_DIR, map_location='cpu'))
NET.eval()
print("load")

dummy = torch.randn(1,3,512,512)

torch.onnx.export(NET, dummy, "sketch.onnx", opset_version=11)
#torch.onnx.export(NET, dummy, "sketch.onnx")

