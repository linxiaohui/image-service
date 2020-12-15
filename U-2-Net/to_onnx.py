import os
import io
import time
import imghdr

import skimage
import torch
from torch.autograd import Variable
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

import zerorpc
import numpy as np
from PIL import Image

from data_loader import RescaleT
from data_loader import ToTensorLab
from data_loader import SalObjDataset

from model import U2NET

MODEL_DIR = os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'u2net.pth')
NET = U2NET(3, 1)
NET.load_state_dict(torch.load(MODEL_DIR, map_location='cpu'))
NET.eval()
print("load")

dummy = torch.randn(1,3,320,320)

torch.onnx.export(NET, dummy, "u2net.onnx")

