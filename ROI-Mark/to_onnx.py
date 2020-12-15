import os
import sys
import imghdr

import cv2
import torch
import numpy as np
import zerorpc

from dm_models import runmodel
from dm_models.BiSeNet_model import BiSeNet

netF = BiSeNet(num_classes=1, context_path='resnet18',train_flag=False)
netF.load_state_dict(torch.load(os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'pretrained_models', 'add_face.pth')))
netF.eval()

dummy = torch.randn(1, 3, 360, 360)


torch.onnx.export(netF, dummy, "face.onnx")



