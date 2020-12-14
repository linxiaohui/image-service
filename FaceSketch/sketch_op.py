# -*- coding: utf-8 -*-
""""
基于[U-2-Net项目](https://github.com/NathanUA/U-2-Net)的u2net_test.py文件修改
定义Sketcher对象， 以期在资源有限的环境中运行时可以按需定义、释放对象
"""
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
from PIL import Image
from PIL import ImageOps

from data_loader import RescaleT
from data_loader import ToTensorLab
from data_loader import SalObjDataset

from model import U2NET

# normalize the predicted SOD probability map
def norm_pred(d):
    ma = torch.max(d)
    mi = torch.min(d)
    dn = (d-mi)/(ma-mi)
    return dn


class SketcherOp(object):
    def __init__(self):
        MODEL_DIR = os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'sketch.pth')
        print("...load sketch---173.6 MB")
        self.NET = U2NET(3, 1)
        # NET.load_state_dict(torch.load(MODEL_DIR,  map_location=lambda storage, loc: storage))
        self.NET.load_state_dict(torch.load(MODEL_DIR, map_location='cpu'))
        if torch.cuda.is_available():
            self.NET.cuda()
        self.NET.eval()

    def gen_output(self, image_name, pred):
        predict = pred
        predict = predict.squeeze()
        predict_np = predict.cpu().data.numpy()
        im = Image.fromarray(predict_np*255).convert('RGB')
        img_name = image_name.split(os.sep)[-1]
        image = skimage.io.imread(image_name)
        imo = im.resize((image.shape[1], image.shape[0]), resample=Image.BILINEAR)
        imo = ImageOps.invert(imo)
        b = io.BytesIO()
        imo.save(b, "png")
        data = b.getvalue()
        return data

    def image_sketch(self, image_data):
        if isinstance(image_data, list):
            image_data_list = image_data
        else:
            image_data_list = [image_data]
        img_name_list = []
        for image_data in image_data_list:
            ext = imghdr.what(None, image_data)
            fn = "{}.{}".format(time.time(), ext)
            with open(fn, "wb") as fp:
                fp.write(image_data)
            img_name_list.append(fn)

        result_list = []
        test_salobj_dataset = SalObjDataset(img_name_list=img_name_list,
                                            lbl_name_list=[],
                                            transform=transforms.Compose([RescaleT(320), ToTensorLab(flag=0)])
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

            d1, d2, d3, d4, d5, d6, d7 = self.NET(inputs_test)
            # normalization
            pred = d1[:, 0, :, :]
            pred = norm_pred(pred)
            dat = self.gen_output(img_name_list[i_test], pred)
            result_list.append(dat)
            del d1, d2, d3, d4, d5, d6, d7

        for fn in img_name_list:
            os.remove(fn)
        return result_list

if __name__ == "__main__":
    s = zerorpc.Server(SketcherOp())
    s.bind("tcp://0.0.0.0:54325")
    s.run()
