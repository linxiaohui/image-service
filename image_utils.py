# -*- coding: utf-8 -*-
import io
import imghdr

from PIL import Image

def image_convert(image_data, convert_type):
    assert convert_type.lower() in ['jpg', 'jpeg', 'webp', 'png', 'gif']
    input_type = imghdr.what(None, image_data)
    im = Image.open(io.BytesIO(image_data))
    if im.mode=="RGBA":
        im.load()  # required for png.split()
        background = Image.new("RGB", im.size, (255, 255, 255))
        background.paste(im, mask=im.split()[3])  # 3 is the alpha channel
        im = background
    b = io.BytesIO()
    if input_type == 'gif':
        im.save(b, convert_type, save_all=True)
    else:
        im.save(b, convert_type)
    data = b.getvalue()
    return data

