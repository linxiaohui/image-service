# -*- coding: utf-8 -*-
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import warnings
warnings.filterwarnings("ignore")
import time
import imghdr

import keras
import numpy as np

def load_images(image_paths, image_size):
    """
    Function for loading images into numpy arrays for passing to model.predict
    inputs:
        image_paths: list of image paths to load
        image_size: size into which images should be resized

    outputs:
        loaded_images: loaded images on which keras model can run predictions
        loaded_image_indexes: paths of images which the function is able to process

    """
    loaded_images = []
    loaded_image_paths = []

    for i, img_path in enumerate(image_paths):
        try:
            image = keras.preprocessing.image.load_img(img_path, target_size = image_size)
            image = keras.preprocessing.image.img_to_array(image)
            image /= 255
            loaded_images.append(image)
            loaded_image_paths.append(img_path)
        except Exception as ex:
            print(i, img_path, ex)
    
    return np.asarray(loaded_images), loaded_image_paths

class KerasPredictor(object):
    """
        Class for loading model and running predictions.
        For example on how to use take a look the if __name__ == '__main__' part.
    """
    nsfw_model = None

    def __init__(self, model_path):
        """
            model = keras_predictor('path_to_weights')
        """
        KerasPredictor.nsfw_model = keras.models.load_model(model_path)

    def predict(self, image_paths=[], batch_size=32, image_size=(299, 299),
                categories=['drawings', 'hentai', 'neutral', 'porn', 'sexy']):
        """
            inputs:
                image_paths: list of image paths or can be a string too (for single image)
                batch_size: batch_size for running predictions
                image_size: size to which the image needs to be resized
                categories: since the model predicts numbers, categories is the list of actual names of categories
        """
        if isinstance(image_paths, str):
            image_paths = [image_paths]
        loaded_images, loaded_image_paths = load_images(image_paths, image_size)
        if not loaded_image_paths:
            return {}
        model_preds = KerasPredictor.nsfw_model.predict(loaded_images, batch_size=batch_size)
        preds = np.argsort(model_preds, axis=1).tolist()
        probs = []
        for i, single_preds in enumerate(preds):
            single_probs = []
            for j, pred in enumerate(single_preds):
                single_probs.append(model_preds[i][pred])
                preds[i][j] = categories[pred]
            
            probs.append(single_probs)

        images_preds = {}
        
        for i, loaded_image_path in enumerate(loaded_image_paths):
            images_preds[loaded_image_path] = {}
            for _ in range(len(preds[i])):
                images_preds[loaded_image_path][preds[i][_]] = float(probs[i][_]) 

        return images_preds


MODEL_PATH = os.path.join(os.environ['IMAGESERVICE_ROOT'], 'models', 'nsfw.299x299.h5')
nsfw_predictor = KerasPredictor(MODEL_PATH)

def nsfw_predict(image_data):
    ext = imghdr.what(None, image_data)
    fn = "{}.{}".format(time.time(), ext)
    with open(fn, "wb") as fp:
        fp.write(image_data)
    result = nsfw_predictor.predict([fn])
    os.remove(fn)
    return result

def nsfw_batch_predict(images):
    """images: [(image_id, image_data),....]"""
    image_list = []
    for _id, _data in images:
        ext = imghdr.what(None, _data)
        fn = f"{_id}.{ext}"
        with open(fn, "wb") as fp:
            fp.write(_data)
        image_list.append(fn)
    ret = nsfw_predictor.predict(image_list)
    for i in image_list:
        os.remove(i)
    return ret
