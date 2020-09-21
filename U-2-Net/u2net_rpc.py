#基于U-2-Net项目的u2net_test.py文件修改
import os
import io
import glob
import time

import skimage
import torch
import torchvision
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms#, utils
# import torch.optim as optim

import zerorpc
import numpy as np
from PIL import Image

from data_loader import RescaleT
from data_loader import ToTensor
from data_loader import ToTensorLab
from data_loader import SalObjDataset

from model import U2NET # full size version 173.6 MB
from model import U2NETP # small version u2net 4.7 MB

# normalize the predicted SOD probability map
def normPRED(d):
    ma = torch.max(d)
    mi = torch.min(d)

    dn = (d-mi)/(ma-mi)

    return dn

def gen_output(image_name,pred):
    predict = pred
    predict = predict.squeeze()
    predict_np = predict.cpu().data.numpy()
    im = Image.fromarray(predict_np*255).convert('RGB')
    img_name = image_name.split(os.sep)[-1]
    image = skimage.io.imread(image_name)
    imo = im.resize((image.shape[1],image.shape[0]),resample=Image.BILINEAR)
    b = io.BytesIO()
    imo.save(b, "png")
    data = b.getvalue()
    return data



MODEL_NAME = 'u2net' #或者选择 u2netp
MODEL_DIR = os.path.join(os.getcwd(), 'model', MODEL_NAME + '.pth')

if(MODEL_NAME == 'u2net'):
    print("...load U2NET---173.6 MB")
    NET = U2NET(3,1)
elif(MODEL_NAME == 'u2netp'):
    print("...load U2NEP---4.7 MB")
    NET = U2NETP(3,1)
#NET.load_state_dict(torch.load(MODEL_DIR,  map_location=lambda storage, loc: storage))
NET.load_state_dict(torch.load(MODEL_DIR,  map_location='cpu'))
if torch.cuda.is_available():
    NET.cuda()
NET.eval()


def image_cutout(image_data, ext='jpg'):
    if isinstance(image_data, list):
        image_data_list = image_data
    else:
        image_data_list = [image_data]
    
    img_name_list = []
    for image_data in image_data_list:
        fn = "{}.{}".format(time.time(), ext)
        with open(fn, "wb") as fp:
            fp.write(image_data)
        img_name_list.append(fn)

    result_list = []    
    test_salobj_dataset = SalObjDataset(img_name_list = img_name_list,
                                        lbl_name_list = [],
                                        transform=transforms.Compose([RescaleT(320),
                                                                        ToTensorLab(flag=0)])
                                        )
    test_salobj_dataloader = DataLoader(test_salobj_dataset,
                                        batch_size=1,
                                        shuffle=False,
                                        num_workers=1)

    for i_test, data_test in enumerate(test_salobj_dataloader):
        inputs_test = data_test['image']
        inputs_test = inputs_test.type(torch.FloatTensor)
        if torch.cuda.is_available():
            inputs_test = Variable(inputs_test.cuda())
        else:
            inputs_test = Variable(inputs_test)

        d1,d2,d3,d4,d5,d6,d7 = NET(inputs_test)
        # normalization
        pred = d1[:,0,:,:]
        pred = normPRED(pred)

        dat = gen_output(img_name_list[i_test],pred)
        result_list.append(dat)
        del d1,d2,d3,d4,d5,d6,d7

    for fn in img_name_list:
        os.remove(fn)

    return result_list

class U2NetCutOut(object):
    def cutout(self, image_data):
        return image_cutout(image_data)


s = zerorpc.Server(U2NetCutOut())
s.bind("tcp://0.0.0.0:54323")
s.run()
