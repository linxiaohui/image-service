# -*- coding: utf-8 -*-
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import hashlib
import base64
import uuid
import json
import sqlite3
import socket
from abc import ABC
from functools import wraps
import imghdr
import platform
if platform.system() == "Windows":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import requests


def get_baidu_score(data):
    return 0

def get_face_plus_score(data):
    return 0

def get_db_conn():
    _conn = sqlite3.connect("/db/image.db")
    return _conn

class IndexHandler(tornado.web.RequestHandler, ABC):
    def get(self, params=None):
        self.render("index.html")

from beauty_predict import beauty_predict
from face_decet_rpc import FaceDetector
FACE_DETECTOR = FaceDetector()
from face_rank import face_detector
class AIBeautyScoreHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("beauty_score.html", image_uuid=None, params=None)
    def post(self, image_uuid=None):
        file_metas = self.request.files.get('image_file', None)
        file_url = self.get_argument("image_url", None)
        if not file_metas and not file_url:
            self.render("beauty_score.html", image_uuid=None, params=None)
        if file_url:
            resp = requests.get(file_url)
            data = resp.content
            filename = file_url
        else:
            for meta in file_metas:
                filename = meta['filename']
                data = meta['body']
        image_landmark, face_rank = face_detector(data)
        scores = beauty_predict(data)
        if len(scores)>0:
            bp_score = scores[0]
        else:
            bp_score = None
        image_rect = FACE_DETECTOR.face_mark(data)
        image_uuid = str(uuid.uuid4())
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        baidu_score = get_baidu_score(data)
        facepp_score = get_face_plus_score(data)
        _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                        (image_uuid, filename, data, "BEAUTY-SCORE"))
        _cursor.execute("""INSERT INTO beauty_score 
                           (image_uuid, image_landmark, image_rect, face_rank, beauty_predict, baidu_score, facepp_score)
                           VALUES (?,?,?,?,?,?,?)""",
                           (image_uuid, image_landmark, image_rect, face_rank, bp_score, baidu_score, facepp_score))
        _conn.commit()
        _conn.close()
        self.render("beauty_score.html", image_uuid=image_uuid, 
                    params=(face_rank, bp_score, baidu_score, facepp_score))

from cartoonize import Cartoonize
CARTOONER = Cartoonize()
class CartoonHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("cartoon.html", image_uuid=image_uuid)
    def post(self, image_uuid=None):
        file_metas = self.request.files.get('image_file', None)
        file_url = self.get_argument("image_url", None)
        if not file_metas and not file_url:
            self.render("cartoon.html", image_uuid=None)
        if file_url:
            resp = requests.get(file_url)
            data = resp.content
            filename = file_url
        else:
            for meta in file_metas:
                filename = meta['filename']
                data = meta['body']
        _data = CARTOONER.cartoonization(data)
        image_uuid = str(uuid.uuid4())
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                        (image_uuid, filename, data, "CARTOON"))
        _cursor.execute("INSERT INTO cartoon (image_uuid, image_cartoon) VALUES (?,?)",
                         (image_uuid, _data))
        _conn.commit()
        self.render("cartoon.html", image_uuid=image_uuid)

from deep_style import DeepMosaic_Style
TRANSFER = DeepMosaic_Style()
from style_transfer import transfer_style
class StyleTransferHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("style_transfer.html", image_uuid=None, style=None, style_uuid=None)
    def post(self, image_uuid=None):
        style = self.get_argument("style", None)
        if not style:
            # 上传图片，没有选择风格
            file_metas = self.request.files.get('image_file', None)
            file_url = self.get_argument("image_url", None)
            if not file_metas and not file_url:
                self.render("style_transfer.html", image_uuid=None, style_uuid=None)
            if file_url:
                resp = requests.get(file_url)
                data = resp.content
                filename = file_url
            else:
                for meta in file_metas:
                    filename = meta['filename']
                    data = meta['body']
            image_uuid = str(uuid.uuid4())
            _conn = get_db_conn()
            _cursor = _conn.cursor()
            _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                            (image_uuid, filename, data, "STYLE-TRANSFER"))
            _conn.commit()
            _conn.close()
            self.render("style_transfer.html", image_uuid=image_uuid, style=None, style_uuid=None)
        else:
            image_uuid = self.get_argument("image_uuid", None)
            _conn = get_db_conn()
            _cursor = _conn.cursor()
            _cursor.execute("SELECT image_data FROM input_image WHERE image_uuid=?", (image_uuid, ))
            image_data = _cursor.fetchone()
            if image_data is None:
                self.set_status(404)
            image_data = image_data[0]
            if style in ['monet','cezanne','vangogh','ukiyoe']:
                _data = TRANSFER.style_transfer(image_data, style)
            else:
                _data = transfer_style(image_data, style)
            style_uuid = str(uuid.uuid4())
            _cursor.execute("INSERT INTO style_transfer (image_uuid, style_uuid, style, image_style) VALUES (?,?,?,?)",
                             (image_uuid, style_uuid, style, _data))
            _conn.commit()
            _conn.close()
            self.render("style_transfer.html", image_uuid=image_uuid, style=style, style_uuid=style_uuid)


from face_sketch import Sketcher
SKETCHER = Sketcher()
class FaceSketchHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("face_sketch.html", image_uuid=image_uuid)
    def post(self, image_uuid=None):
        file_metas = self.request.files.get('image_file', None)
        file_url = self.get_argument("image_url", None)
        if not file_metas and not file_url:
            self.render("face_sketch.html", image_uuid=None)
        if file_url:
            resp = requests.get(file_url)
            data = resp.content
            filename = file_url
        else:
            for meta in file_metas:
                filename = meta['filename']
                data = meta['body']
        _data = SKETCHER.face_sketch(data)[0]
        image_uuid = str(uuid.uuid4())
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                        (image_uuid, filename, data, "SKETCH"))
        _cursor.execute("INSERT INTO sketch (image_uuid, image_sketch) VALUES (?,?)",
                         (image_uuid, _data))
        _conn.commit()
        self.render("face_sketch.html", image_uuid=image_uuid)

from chg_bg import change_background
class CertPhotoHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("cert_photo.html", image_uuid=None, cert_uuid=None)
    def post(self, image_uuid=None):
        bg_color = self.get_argument("bg_color", None)
        if not bg_color:
            file_metas = self.request.files.get('image_file', None)
            file_url = self.get_argument("image_url", None)
            if not file_metas and not file_url:
                self.render("cert_photo.html", image_uuid=None, style_uuid=None)
            if file_url:
                resp = requests.get(file_url)
                data = resp.content
                filename = file_url
            else:
                for meta in file_metas:
                    filename = meta['filename']
                    data = meta['body']
            image_uuid = str(uuid.uuid4())
            _conn = get_db_conn()
            _cursor = _conn.cursor()
            _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                            (image_uuid, filename, data, "CHANGE-BGCOLOR"))
            _conn.commit()
            _conn.close()
            self.render("cert_photo.html", image_uuid=image_uuid, cert_uuid=None)
        else:
            image_uuid = self.get_argument("image_uuid", None)
            _conn = get_db_conn()
            _cursor = _conn.cursor()
            _cursor.execute("SELECT image_data FROM input_image WHERE image_uuid=?", (image_uuid, ))
            image_data = _cursor.fetchone()
            if image_data is None:
                self.set_status(404)
            image_data = image_data[0]
            _data = change_background(image_data, bg_color)[0]
            cert_uuid = str(uuid.uuid4())
            _cursor.execute("INSERT INTO cert_photo (image_uuid, cert_uuid, bg_color, image_cert) VALUES (?,?,?,?)",
                             (image_uuid, cert_uuid, bg_color, _data))
            _conn.commit()
            _conn.close()
            self.render("cert_photo.html", image_uuid=image_uuid, cert_uuid=cert_uuid)

from inference import face_cartoonization
class FaceCartoonHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("face_cartoon.html", image_uuid=image_uuid)
    def post(self, image_uuid=None):
        file_metas = self.request.files.get('image_file', None)
        file_url = self.get_argument("image_url", None)
        if not file_metas and not file_url:
            self.render("face_cartoon.html", image_uuid=None)
        if file_url:
            resp = requests.get(file_url)
            data = resp.content
            filename = file_url
        else:
            for meta in file_metas:
                filename = meta['filename']
                data = meta['body']
        _data = face_cartoonization(data)
        image_uuid = str(uuid.uuid4())
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                        (image_uuid, filename, data, "FACE-CARTOON"))
        _cursor.execute("INSERT INTO cartoon (image_uuid, image_cartoon) VALUES (?,?)",
                         (image_uuid, _data))
        _conn.commit()
        self.render("face_cartoon.html", image_uuid=image_uuid)

from mosaic_nsfw import nsfw_mosaic_region
class NSFWMosiacHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("nsfw_mosaic.html", image_uuid=image_uuid)
    def post(self, image_uuid=None):
        file_metas = self.request.files.get('image_file', None)
        file_url = self.get_argument("image_url", None)
        if not file_metas and not file_url:
            self.render("nsfw_mosaic.html", image_uuid=None)
        if file_url:
            resp = requests.get(file_url)
            data = resp.content
            filename = file_url
        else:
            for meta in file_metas:
                filename = meta['filename']
                data = meta['body']
        _data =  nsfw_mosaic_region(data)
        image_uuid = str(uuid.uuid4())
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                        (image_uuid, filename, data, "NSFW-MOSAIC"))
        _cursor.execute("INSERT INTO nsfw_mosaic (image_uuid, image_mosaic) VALUES (?,?)",
                         (image_uuid, _data))
        _conn.commit()
        self.render("nsfw_mosaic.html", image_uuid=image_uuid)

from u2net_rpc import image_cutout
class ForeGroundHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("fore_ground.html", image_uuid=image_uuid)
    def post(self, image_uuid=None):
        file_metas = self.request.files.get('image_file', None)
        file_url = self.get_argument("image_url", None)
        if not file_metas and not file_url:
            self.render("fore_ground.html", image_uuid=None)
        if file_url:
            resp = requests.get(file_url)
            data = resp.content
            filename = file_url
        else:
            for meta in file_metas:
                filename = meta['filename']
                data = meta['body']
        _data = image_cutout(data)[0]
        image_uuid = str(uuid.uuid4())
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                        (image_uuid, filename, data, "FORE-GROUND"))
        _cursor.execute("INSERT INTO fore_ground (image_uuid, image_fg) VALUES (?,?)",
                        (image_uuid, _data))
        _conn.commit()
        self.render("fore_ground.html", image_uuid=image_uuid)

from nsfw_predict import nsfw_predict
class NSFWScoreHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("nsfw_score.html", image_uuid=None, score=None)
    def post(self, image_uuid=None):
        file_metas = self.request.files.get('image_file', None)
        file_url = self.get_argument("image_url", None)
        if not file_metas and not file_url:
            self.render("nsfw_score.html", image_uuid=None, score=None)
        if file_url:
            resp = requests.get(file_url)
            data = resp.content
            filename = file_url
        else:
            for meta in file_metas:
                filename = meta['filename']
                data = meta['body']
        scores = nsfw_predict(data, 'png')
        for k in scores:
            score = scores[k]
        image_uuid = str(uuid.uuid4())
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                        (image_uuid, filename, data, "NSFW-SCORE"))
        _conn.commit()
        score = sorted(score.items(), key=lambda x:x[1], reverse=True)
        self.render("nsfw_score.html", image_uuid=image_uuid, score=score)


from roi_marker import DeepMosaics_ROIMarker
ROI_MARKER = DeepMosaics_ROIMarker()
class ROIMarkHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("roi_mark.html", image_uuid=None, roi_uuid=None)
    def post(self, image_uuid=None):
        roi_type = self.get_argument("roi_type", None)
        if not roi_type:
            file_metas = self.request.files.get('image_file', None)
            file_url = self.get_argument("image_url", None)
            if not file_metas and not file_url:
                self.render("roi_mark.html", image_uuid=None, roi_uuid=None)
            if file_url:
                resp = requests.get(file_url)
                data = resp.content
                filename = file_url
            else:
                for meta in file_metas:
                    filename = meta['filename']
                    data = meta['body']
            image_uuid = str(uuid.uuid4())
            _conn = get_db_conn()
            _cursor = _conn.cursor()
            _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                            (image_uuid, filename, data, "ROI-MARK"))
            _conn.commit()
            _conn.close()
            self.render("roi_mark.html", image_uuid=image_uuid, roi_uuid=None)
        else:
            image_uuid = self.get_argument("image_uuid", None)
            _conn = get_db_conn()
            _cursor = _conn.cursor()
            _cursor.execute("SELECT image_data FROM input_image WHERE image_uuid=?", (image_uuid, ))
            image_data = _cursor.fetchone()
            if image_data is None:
                self.set_status(404)
            image_data = image_data[0]
            if roi_type == 'F':
                roi_type = 'face'
            _data = ROI_MARKER.roi_marker(image_data, roi_type)
            roi_uuid = str(uuid.uuid4())
            _cursor.execute("INSERT INTO roi_mark (image_uuid, roi_uuid, roi_type, image_roi) VALUES (?,?,?,?)",
                             (image_uuid, roi_uuid, roi_type, _data))
            _conn.commit()
            _conn.close()
            self.render("roi_mark.html", image_uuid=image_uuid, roi_uuid=roi_uuid)

from deep_mosaic import DeepMosaics_Mosaic
ROI_MOSAICOR = DeepMosaics_Mosaic()
class ROIMosaicHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("roi_mosaic.html", image_uuid=None, roi_uuid=None)
    def post(self, image_uuid=None):
        roi_type = self.get_argument("roi_type", None)
        if not roi_type:
            file_metas = self.request.files.get('image_file', None)
            file_url = self.get_argument("image_url", None)
            if not file_metas and not file_url:
                self.render("roi_mosaic.html", image_uuid=None, roi_uuid=None)
            if file_url:
                resp = requests.get(file_url)
                data = resp.content
                filename = file_url
            else:
                for meta in file_metas:
                    filename = meta['filename']
                    data = meta['body']
            image_uuid = str(uuid.uuid4())
            _conn = get_db_conn()
            _cursor = _conn.cursor()
            _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                            (image_uuid, filename, data, "ROI-MARK"))
            _conn.commit()
            _conn.close()
            self.render("roi_mosaic.html", image_uuid=image_uuid, roi_uuid=None)
        else:
            image_uuid = self.get_argument("image_uuid", None)
            _conn = get_db_conn()
            _cursor = _conn.cursor()
            _cursor.execute("SELECT image_data FROM input_image WHERE image_uuid=?", (image_uuid, ))
            image_data = _cursor.fetchone()
            if image_data is None:
                self.set_status(404)
            image_data = image_data[0]
            if roi_type == 'F':
                roi_type = 'face'
            _data = ROI_MOSAICOR.deep_mosaic(image_data, roi_type)
            roi_uuid = str(uuid.uuid4())
            _cursor.execute("INSERT INTO roi_mark (image_uuid, roi_uuid, roi_type, image_roi) VALUES (?,?,?,?)",
                            (image_uuid, roi_uuid, roi_type, _data))
            _conn.commit()
            _conn.close()
            self.render("roi_mosaic.html", image_uuid=image_uuid, roi_uuid=roi_uuid)

from mosaic_utils import domosaic
class MosaicAppHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("mosaic_app.html", image_uuid=None)
    def post(self, image_uuid=None):
        file_metas = self.request.files.get('image_file', None)
        file_url = self.get_argument("image_url", None)
        if not file_metas and not file_url:
            self.render("mosaic_app.html", image_uuid=None, roi_uuid=None)
        if file_url:
            resp = requests.get(file_url)
            data = resp.content
            filename = file_url
        else:
            for meta in file_metas:
                filename = meta['filename']
                data = meta['body']
        image_uuid = str(uuid.uuid4())
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                        (image_uuid, filename, data, "MOSAIC-APP"))
        _cursor.execute("INSERT INTO mosaic_app (image_uuid, mosaic_uuid, image_mosaic) VALUES (?,?,?)",
                        (image_uuid, image_uuid, data))
        _conn.commit()
        _conn.close()
        self.render("mosaic_app.html", image_uuid=image_uuid)

import image_utils
class ImgCovertHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("image_convert.html", image_uuid=None, convert_uuid=None)
    def post(self, image_uuid=None):
        convert_type = self.get_argument("convert_type", None)
        if not convert_type:
            file_metas = self.request.files.get('image_file', None)
            file_url = self.get_argument("image_url", None)
            if not file_metas and not file_url:
                self.render("image_convert.html", image_uuid=None, convert_uuid=None)
            if file_url:
                resp = requests.get(file_url)
                data = resp.content
                filename = file_url
            else:
                for meta in file_metas:
                    filename = meta['filename']
                    data = meta['body']
            image_uuid = str(uuid.uuid4())
            _conn = get_db_conn()
            _cursor = _conn.cursor()
            _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                            (image_uuid, filename, data, "CONVERT"))
            _conn.commit()
            _conn.close()
            self.render("image_convert.html", image_uuid=image_uuid, convert_uuid=None)
        else:
            image_uuid = self.get_argument("image_uuid", None)
            _conn = get_db_conn()
            _cursor = _conn.cursor()
            _cursor.execute("SELECT image_data FROM input_image WHERE image_uuid=?", (image_uuid, ))
            image_data = _cursor.fetchone()
            if image_data is None:
                self.set_status(404)
            image_data = image_data[0]
            _data = image_utils.image_convert(image_data, convert_type)
            convert_uuid = str(uuid.uuid4())
            _cursor.execute("INSERT INTO image_convert (image_uuid, convert_uuid, conv_type, image_converted) VALUES (?,?,?,?)",
                            (image_uuid, convert_uuid, convert_type, _data))
            _conn.commit()
            _conn.close()
            self.render("image_convert.html", image_uuid=image_uuid, convert_uuid=convert_uuid)


class AsciiHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("ascii.html", image_uuid=None)


class ImageHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_type, image_uuid):
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        if image_type == 'input':
            _cursor.execute("SELECT image_data FROM  input_image WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'cartoon':
            _cursor.execute("SELECT image_cartoon FROM cartoon WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'style':
            _cursor.execute("SELECT image_style FROM style_transfer WHERE style_uuid=?",(image_uuid,))
        elif image_type == 'sketch':
            _cursor.execute("SELECT image_sketch FROM sketch WHERE image_uuid=?",(image_uuid,))
        elif image_type == 'cert':
            _cursor.execute("SELECT image_cert FROM cert_photo WHERE cert_uuid=?", (image_uuid, ))
        elif image_type == 'nsfw_mosaic':
            _cursor.execute("SELECT image_mosaic FROM nsfw_mosaic WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'land_mark':
            _cursor.execute("SELECT image_landmark FROM beauty_score WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'face_box':
            _cursor.execute("SELECT image_rect FROM beauty_score WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'fore_ground':
            _cursor.execute("SELECT image_fg FROM fore_ground WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'roi_mark':
            _cursor.execute("SELECT image_roi FROM roi_mark WHERE roi_uuid=?", (image_uuid,))
        elif image_type == 'convert':
            _cursor.execute("SELECT image_converted FROM image_convert WHERE image_uuid=?", (image_uuid,))
        image = _cursor.fetchone()
        _conn.close()
        if image:
            content_type = imghdr.what(None, image[0])
            self.set_header("Content-Type", "image/"+content_type)
            self.write(image[0])
        else:
            self.set_status(404)

class ImageMosaicHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid, region):
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        _cursor.execute("SELECT image_mosaic FROM mosaic_app WHERE mosaic_uuid=?", (image_uuid,))
        image = _cursor.fetchone()
        if image:
            image_data = image[0]
            left, top, right, down = [int(_) for _ in region.split("px")[0:4]]
            width = abs(left-right)
            height = abs(top-down)
            if left > right:
                left = right
            if top > down:
                top = down
            _data = domosaic(image_data, (left, top, width, height))
            _cursor.execute("UPDATE mosaic_app SET image_mosaic=? WHERE mosaic_uuid=?", (_data, image_uuid))
            _conn.commit()
            _conn.close()
            self.write(_data)
        else:
            _conn.close()
            self.set_status(404)

class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "imgsvr_templates"),
            static_path=os.path.join(os.path.dirname(__file__), "imgsvr_static"),
            xsrf_cookies=False,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            autoescape=None,
        )
        handlers = [
            (r"/", IndexHandler),
            (r"/index.html/?(.*)", IndexHandler),
            (r"/beauty_score.html/?(.*)", AIBeautyScoreHandler),
            (r"/cartoon.html/?(.*)", CartoonHandler),
            (r"/face_cartoon.html/?(.*)", FaceCartoonHandler),
            (r"/face_sketch.html/?(.*)", FaceSketchHandler),
            (r"/style_transfer.html/?(.*)", StyleTransferHandler),
            (r"/fore_ground.html/?(.*)", ForeGroundHandler),
            (r"/cert_photo.html/?(.*)", CertPhotoHandler),
            (r"/mosaic_app.html/?(.*)", MosaicAppHandler),
            (r"/nsfw_mosaic.html/?(.*)", NSFWMosiacHandler),
            (r"/roi_mosaic.html/?(.*)", ROIMosaicHandler),
            (r"/nsfw.html/?(.*)", NSFWScoreHandler),
            (r"/roi_mark.html/?(.*)", ROIMarkHandler),
            (r"/convert.html/?(.*)", ImgCovertHandler),
            (r"/ascii.html/?(.*)", AsciiHandler),
            (r"/image/(.+)/(.+)", ImageHandler),
            (r"/mosaic/(.+)/(.+)", ImageMosaicHandler),
            (r"/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(80)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except Exception as e:
        print(e)
        tornado.ioloop.IOLoop.instance().stop()

if __name__ == "__main__":
    try:
        os.mkdir("/db")
    except:
        pass
    try:
        conn = get_db_conn()
        conn.execute("""CREATE TABLE input_image (image_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                                  image_uuid char(36), 
                                                  file_name TEXT,
                                                  image_data BLOB,
                                                  params TEXT,
                                                  insert_time datetime default current_timestamp)
        """)
        conn.execute("""CREATE TABLE beauty_score (image_uuid char(36), 
                                                   image_landmark BLOB, 
                                                   image_rect BLOB,
                                                   face_rank float,
                                                   beauty_predict float,
                                                   baidu_score float,
                                                   facepp_score float)
        """)
        conn.execute("""CREATE TABLE cartoon (image_uuid char(36), 
                                              image_cartoon BLOB)
        """)
        conn.execute("""CREATE TABLE sketch (image_uuid char(36), 
                                             image_sketch BLOB)
        """)
        conn.execute("""CREATE TABLE style_transfer (image_uuid char(36),
                                                     style_uuid char(36),
                                                     style TEXT,
                                                     image_style BLOB)
        """)
        conn.execute("""CREATE TABLE cert_photo (image_uuid char(36),
                                                 cert_uuid char(36),
                                                 bg_color TEXT,
                                                 image_cert BLOB)
        """)
        conn.execute("""CREATE TABLE nsfw_mosaic (image_uuid char(36),
                                                  image_mosaic BLOB)
        """)
        conn.execute("""CREATE TABLE fore_ground (image_uuid char(36), 
                                                  image_fg BLOB)
        """)
        conn.execute("""CREATE TABLE roi_mark (image_uuid char(36),
                                               roi_uuid char(36),
                                               roi_type TEXT,
                                               image_roi BLOB)
        """)
        conn.execute("""CREATE TABLE mosaic_app (image_uuid char(36),
                                                 mosaic_uuid char(36),
                                                 image_mosaic BLOB)
        """)
        conn.execute("""CREATE TABLE image_convert (image_uuid char(36),
                                                    convert_uuid char(36),
                                                    conv_type TEXT,
                                                    image_converted BLOB)
        """)
    except Exception as ex:
        print(ex)
    try:
        csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        csock.connect(('8.8.8.8', 80))
        (addr, port) = csock.getsockname()
        csock.close()
        print(addr)
    except socket.error:
        print(socket.gethostbyname_ex(socket.gethostname()))
    main()
