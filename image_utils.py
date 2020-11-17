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


ASCII_CHARS = [ '#', '?', '%', '.', 'S', '+', '.', '*', ':', ',', '@']
def scale_image(image, new_width=100):
    """
    Resizes an image preserving the aspect ratio.
    """
    (original_width, original_height) = image.size
    aspect_ratio = original_height/float(original_width)
    new_height = int(aspect_ratio * new_width)

    new_image = image.resize((new_width, new_height))
    return new_image

def convert_to_grayscale(image):
    return image.convert('L')

def map_pixels_to_ascii_chars(image, range_width=25):
    """
    Maps each pixel to an ascii char based on the range
    in which it lies.

    0-255 is divided into 11 ranges of 25 pixels each.
    """

    pixels_in_image = list(image.getdata())
    pixels_to_chars = [ASCII_CHARS[pixel_value//range_width] for pixel_value in
            pixels_in_image]

    return "".join(pixels_to_chars)

def convert_image_to_ascii(image_data, new_width=100):
    image = Image.open(io.BytesIO(image_data))
    image = scale_image(image)
    image = convert_to_grayscale(image)

    pixels_to_chars = map_pixels_to_ascii_chars(image)
    len_pixels_to_chars = len(pixels_to_chars)

    image_ascii = [pixels_to_chars[index: index + new_width] for index in
            range(0, len_pixels_to_chars, new_width)]

    return "\n".join(image_ascii)

