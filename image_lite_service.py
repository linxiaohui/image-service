# -*- coding: utf-8 -*-
import os
import base64
import uuid
import json
import sqlite3
import socket
from abc import ABC
import imghdr
import platform
import urllib3
import gc

urllib3.disable_warnings()
if platform.system() == "Windows":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import requests

def get_db_conn():
    _conn = sqlite3.connect(os.path.join(os.environ['IMAGESERVICE_ROOT'], "db", "image.db"))
    return _conn

def get_baidu_score(image_uuid, data):
    _conn = get_db_conn()
    _cursor = _conn.cursor()
    _score = -1
    try:
        ak = os.environ['BAIDU_AIP_AK']
        sk = os.environ['BAIDU_AIP_SK']
    except Exception as e1:
        print("没有配置Baidu AI平台的Key", e1)
        return 0
    host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={ak}&client_secret={sk}'
    try:
        response = requests.get(host)
        if response:
            access_k = response.json()['access_token']
            request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
            options = {
                'image_type': 'BASE64',
                'image': base64.b64encode(data).decode('UTF-8'),
                'face_field': 'age,beauty,expression,face_shape,gender,glasses,landmark,landmark72,landmark150,race,quality,eye_status,emotion,face_type'
            }
            request_url = request_url + "?access_token=" + access_k
            headers = {'content-type': 'application/json'}
            resp = requests.post(request_url, data=options, headers=headers)
            if resp:
                aip_return = resp.content
                _cursor.execute("INSERT INTO baidu_aip_result (image_uuid, aip_return) VALUES (?,?)", (image_uuid, aip_return))
                ret_json = json.loads(aip_return)
                _score = ret_json['result']['face_list'][0]['beauty']
    except Exception as e2:
        print("调用Baidu AI平台API错", e2)
        _score = -1
    _conn.commit()
    _conn.close()
    return _score

def get_face_plus_score(image_uuid, data):
    _conn = get_db_conn()
    _cursor = _conn.cursor()
    _score = -1
    try:
        ak = os.environ['FACEPP_AK']
        sk = os.environ['FACEPP_SK']
    except Exception as e3:
        print("没有配置旷视AI平台的Key", e3)
        return 0
    host = "https://api-cn.faceplusplus.com/facepp/v3/detect"
    req_data = {'api_key': ak,
                'api_secret': sk,
                'image_base64': base64.b64encode(data).decode('UTF-8'),
                'return_attributes': 'gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus',
                'return_landmark': '2'
                }
    try:
        resp = requests.post(host, data=req_data)
        if resp:
            facepp_return = resp.content
            _cursor.execute("INSERT INTO facepp_result (image_uuid, facepp_return) VALUES (?,?)",
                            (image_uuid, facepp_return))
            ret_json = json.loads(facepp_return)
            _score = ret_json['faces'][0]['attributes']['beauty']['male_score']
    except Exception as e4:
        print("调用旷视API错", e4)
        _score = -1
    _conn.commit()
    _conn.close()
    return _score

class IndexHandler(tornado.web.RequestHandler, ABC):
    def get(self, params=None):
        self.render("index.html")

from face_detect_rpc import FaceDetector
from facerank_op import FaceRankOp
from beauty_predict_cv2 import BeautyPredictCV2
from mtcnn_cv2 import MTCNN
from face_marker_cv2 import FaceMarkerCV2
class AIBeautyScoreHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("beauty_score.html", image_uuid=None, params=None)

    def post(self, image_uuid=None):
        file_metas = self.request.files.get('image_file', None)
        file_url = self.get_argument("image_url", None)
        if not file_metas and not file_url:
            self.render("beauty_score.html", image_uuid=None, params=None)
        if file_url:
            resp = requests.get(file_url, verify=False)
            data = resp.content
            filename = file_url
        else:
            for meta in file_metas:
                filename = meta['filename']
                data = meta['body']
        # dlib landmark
        facerank_op = FaceRankOp()
        dlib_landmark, face_rank = facerank_op.face_detector(data)
        del facerank_op
        # dlib face_detector
        bp_op = BeautyPredictCV2()
        scores, dlib_face = bp_op.beauty_score(data)
        del bp_op
        if len(scores) > 0:
            bp_score = scores[0]
        else:
            bp_score = None
        # OpenCV
        face_detct = FaceDetector()
        opencv_face = face_detct.face_mark(data)
        del face_detct
        # FaceNet MTCNN
        mtcnn_net = MTCNN()
        mtcnn_face = mtcnn_net.mark_faces(data)
        del mtcnn_net
        # DeepMosaic Face
        face_marker = FaceMarkerCV2()
        deepmosaic_face = face_marker.face_marker(data)
        del face_marker
        image_uuid = str(uuid.uuid4())
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        baidu_score = get_baidu_score(image_uuid, data)
        facepp_score = get_face_plus_score(image_uuid, data)
        _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                        (image_uuid, filename, data, "BEAUTY-SCORE"))
        _cursor.execute("""INSERT INTO beauty_score 
                           (image_uuid, dlib_landmark, dlib_face, opencv_face, mtcnn_face, deepmosaic_face, face_rank, beauty_predict, baidu_score, facepp_score)
                           VALUES (?,?,?,?,?,?,?,?,?,?)""",
                           (image_uuid, dlib_landmark, dlib_face, opencv_face, mtcnn_face, deepmosaic_face, face_rank, bp_score, baidu_score, facepp_score))
        _conn.commit()
        _conn.close()
        self.render("beauty_score.html", image_uuid=image_uuid, 
                    params=(face_rank, bp_score, baidu_score, facepp_score))
        gc.collect()

from cartoon_onnx import ONNXModel as CartoonONNX
class CartoonHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("cartoon.html", image_uuid=image_uuid)

    def post(self, image_uuid=None):
        file_metas = self.request.files.get('image_file', None)
        file_url = self.get_argument("image_url", None)
        if not file_metas and not file_url:
            self.render("cartoon.html", image_uuid=None)
        if file_url:
            resp = requests.get(file_url, verify=False)
            data = resp.content
            filename = file_url
        else:
            for meta in file_metas:
                filename = meta['filename']
                data = meta['body']
        cartoon_net = CartoonONNX()
        _data = cartoon_net.cartoon(data)
        del cartoon_net
        image_uuid = str(uuid.uuid4())
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                        (image_uuid, filename, data, "CARTOON"))
        _cursor.execute("INSERT INTO cartoon (image_uuid, image_cartoon) VALUES (?,?)",
                         (image_uuid, _data))
        _conn.commit()
        self.render("cartoon.html", image_uuid=image_uuid)

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
                resp = requests.get(file_url, verify=False)
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
            _data = transfer_style(image_data, style)
            style_uuid = str(uuid.uuid4())
            _cursor.execute("INSERT INTO style_transfer (image_uuid, style_uuid, style, image_style) VALUES (?,?,?,?)",
                             (image_uuid, style_uuid, style, _data))
            _conn.commit()
            _conn.close()
            self.render("style_transfer.html", image_uuid=image_uuid, style=style, style_uuid=style_uuid)

from face_sketch_cv2 import FaceSketcherCV2
class FaceSketchHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("face_sketch.html", image_uuid=image_uuid)

    def post(self, image_uuid=None):
        file_metas = self.request.files.get('image_file', None)
        file_url = self.get_argument("image_url", None)
        if not file_metas and not file_url:
            self.render("face_sketch.html", image_uuid=None)
        if file_url:
            resp = requests.get(file_url, verify=False)
            data = resp.content
            filename = file_url
        else:
            for meta in file_metas:
                filename = meta['filename']
                data = meta['body']
        op = FaceSketcherCV2()
        _data = op.face_sketch(data)
        del op
        image_uuid = str(uuid.uuid4())
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                        (image_uuid, filename, data, "SKETCH"))
        _cursor.execute("INSERT INTO sketch (image_uuid, image_sketch) VALUES (?,?)",
                         (image_uuid, _data))
        _conn.commit()
        self.render("face_sketch.html", image_uuid=image_uuid)

from u2net_cv2 import U2NetCV2
class ForeGroundHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("fore_ground.html", image_uuid=image_uuid)

    def post(self, image_uuid=None):
        file_metas = self.request.files.get('image_file', None)
        file_url = self.get_argument("image_url", None)
        if not file_metas and not file_url:
            self.render("fore_ground.html", image_uuid=None)
        if file_url:
            resp = requests.get(file_url, verify=False)
            data = resp.content
            filename = file_url
        else:
            for meta in file_metas:
                filename = meta['filename']
                data = meta['body']
        op = U2NetCV2()
        _data = op.image_cutout(data)
        del op
        image_uuid = str(uuid.uuid4())
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        _cursor.execute("INSERT INTO input_image (image_uuid, file_name, image_data, params) VALUES (?,?,?,?)",
                        (image_uuid, filename, data, "FORE-GROUND"))
        _cursor.execute("INSERT INTO fore_ground (image_uuid, image_fg) VALUES (?,?)",
                        (image_uuid, _data))
        _conn.commit()
        self.render("fore_ground.html", image_uuid=image_uuid)

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
            resp = requests.get(file_url, verify=False)
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
class ImgConvertHandler(tornado.web.RequestHandler, ABC):
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
                resp = requests.get(file_url, verify=False)
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
        self.render("ascii.html", image_uuid=None, ascii_code=None)

    def post(self, image_uuid=None):
        file_metas = self.request.files.get('image_file', None)
        file_url = self.get_argument("image_url", None)
        if not file_metas and not file_url:
            self.render("ascii.html", image_uuid=None, ascii_code=None)
        if file_url:
            resp = requests.get(file_url, verify=False)
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
                        (image_uuid, filename, data, "ASCII"))
        _conn.commit()
        _conn.close()
        ascii_code = image_utils.convert_image_to_ascii(data)
        self.render("ascii.html", image_uuid=image_uuid, ascii_code=ascii_code)

class ImageHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_type, image_uuid):
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        if image_type == 'input':
            _cursor.execute("SELECT image_data FROM  input_image WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'cartoon':
            _cursor.execute("SELECT image_cartoon FROM cartoon WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'style':
            _cursor.execute("SELECT image_style FROM style_transfer WHERE style_uuid=?", (image_uuid,))
        elif image_type == 'sketch':
            _cursor.execute("SELECT image_sketch FROM sketch WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'cert':
            _cursor.execute("SELECT image_cert FROM cert_photo WHERE cert_uuid=?", (image_uuid, ))
        elif image_type == 'land_mark':
            _cursor.execute("SELECT dlib_landmark FROM beauty_score WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'dlib_face':
            _cursor.execute("SELECT dlib_face FROM beauty_score WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'dm_face':
            _cursor.execute("SELECT deepmosaic_face FROM beauty_score WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'face_box':
            _cursor.execute("SELECT opencv_face FROM beauty_score WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'face_net':
            _cursor.execute("SELECT mtcnn_face FROM beauty_score WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'fore_ground':
            _cursor.execute("SELECT image_fg FROM fore_ground WHERE image_uuid=?", (image_uuid,))
        elif image_type == 'convert':
            _cursor.execute("SELECT image_converted FROM image_convert WHERE convert_uuid=?", (image_uuid,))
        elif image_type == 'mosaic':
            _cursor.execute("SELECT image_mosaic FROM mosaic_app WHERE mosaic_uuid=?", (image_uuid,))
        image = _cursor.fetchone()
        _conn.close()
        if image:
            content_type = imghdr.what(None, image[0])
            self.set_header("Content-Type", "image/"+content_type)
            self.write(image[0])
        else:
            self.set_status(404)

class ImageMosaicHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid, region=None):
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        if region is None:
            # 恢复
            _cursor.execute("SELECT image_data FROM  input_image WHERE image_uuid=?", (image_uuid,))
            rec = _cursor.fetchone()
            if rec is None:
                _conn.close()
                self.set_status(404)
            else:
                _data = rec[0]
                _cursor.execute("UPDATE mosaic_app SET image_mosaic=? WHERE mosaic_uuid=?", (_data, image_uuid))
                _conn.commit()
                _conn.close()
                self.write(_data)
        else:
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
            template_path=os.path.join(os.path.dirname(__file__), "imgsvr_lite_templates"),
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
            (r"/style_transfer.html/?(.*)", StyleTransferHandler),
            (r"/face_sketch.html/?(.*)", FaceSketchHandler),
            (r"/fore_ground.html/?(.*)", ForeGroundHandler),
            (r"/mosaic_app.html/?(.*)", MosaicAppHandler),
            (r"/convert.html/?(.*)", ImgConvertHandler),
            (r"/ascii.html/?(.*)", AsciiHandler),
            (r"/image/(.+)/(.+)", ImageHandler),
            (r"/mosaic/(.+)/(.+)", ImageMosaicHandler),
            (r"/mosaic/(.+)", ImageMosaicHandler),
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
        os.mkdir(os.path.join(os.environ['IMAGESERVICE_ROOT'], 'db'))
    except Exception as e:
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
                                                   dlib_landmark BLOB, 
                                                   dlib_face BLOB,
                                                   opencv_face BLOB,
                                                   mtcnn_face BLOB,
                                                   deepmosaic_face BLOB,
                                                   face_rank float,
                                                   beauty_predict float,
                                                   baidu_score float,
                                                   facepp_score float)
        """)
        conn.execute("""CREATE TABLE baidu_aip_result(image_uuid char(36),
                                                      aip_return TEXT)
        """)
        conn.execute("""CREATE TABLE facepp_result(image_uuid char(36),
                                                   facepp_return TEXT)
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
        conn.execute("""CREATE TABLE fore_ground (image_uuid char(36), 
                                                  image_fg BLOB)
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
