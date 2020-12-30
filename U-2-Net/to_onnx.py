import os
import sys
import io
import time
import imghdr

import skimage
import torch
import torch.quantization
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

MODEL_DIR = sys.argv[1]
NET = U2NET(3, 1)
NET.load_state_dict(torch.load(MODEL_DIR, map_location='cpu'))
NET.eval()
print("load")

# NET = torch.quantization.quantize_dynamic(NET, dtype=torch.int8)

dummy = torch.randn(1,3,320,320)

torch.onnx.export(NET, dummy, sys.argv[2], do_constant_folding=True)

