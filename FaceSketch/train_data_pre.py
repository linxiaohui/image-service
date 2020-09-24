# -*- coding: utf-8 -*-
import os
import sys

from PIL import Image

DATA_DIR = sys.argv[1]

def split_image(fn_path):
    img = Image.open(fn_path)
    fn = fn_path.split(os.sep)[-1].strip(".png")
    train_fn = fn+"_train.png"
    label_fn = fn+"_label.png"
    cropped = img.crop((0, 0, 512, 512))  # (left, upper, right, lower)
    cropped.save(train_fn)
    cropped = img.crop((512, 0, 1024, 512))  # (left, upper, right, lower)
    cropped.save(label_fn)

os.chdir(DATA_DIR)
for f in os.listdir("."):
    split_image(f)


