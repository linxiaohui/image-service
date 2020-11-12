# -*- coding: utf-8 -*-
import os
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

def get_db_conn():
    _conn = sqlite3.connect("/db/image.db")
    return _conn

class IndexHandler(tornado.web.RequestHandler, ABC):
    def get(self, params=None):
        self.render("index.html")

class AIBeautyScoreHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid=None):
        self.render("beauty_score.html")

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
                _data = TRANSFER.style_transfer(data, style)
            else:
                _data = transfer_style(image_data, style)
            style_uuid = str(uuid.uuid4())
            _cursor.execute("INSERT INTO style_transfer (image_uuid, style_uuid, style, image_style) VALUES (?,?,?,?)",
                             (image_uuid, style_uuid, style, _data))
            _conn.commit()
            _conn.close()
            self.render("style_transfer.html", image_uuid=image_uuid, style=style, style_uuid=style_uuid)


class ImageHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_type, image_uuid):
        _conn = get_db_conn()
        _cursor = _conn.cursor()
        if image_type=='input':
            _cursor.execute("SELECT image_data FROM  input_image WHERE image_uuid=?", (image_uuid,))
        elif image_type=='cartoon':
            _cursor.execute("SELECT image_cartoon FROM cartoon WHERE image_uuid=?", (image_uuid,))
        image = _cursor.fetchone()
        _conn.close()
        if image:
            self.write(image[0])
        else:
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
            (r"/face_cartoon.html/?(.*)", AIBeautyScoreHandler),
            (r"/face_sketch.html/?(.*)", AIBeautyScoreHandler),
            (r"/style_transfer.html/?(.+)", StyleTransferHandler),
            (r"/fore_ground.html/?(.+)", AIBeautyScoreHandler),
            (r"/cert_photo.html/?(.+)", AIBeautyScoreHandler),
            (r"/mosaic_app.html/?(.+)", AIBeautyScoreHandler),
            (r"/nsfw_mosaic.html/?(.+)", AIBeautyScoreHandler),
            (r"/roi_mosaic.html/?(.+)", AIBeautyScoreHandler),
            (r"/nsfw.html/?(.+)", AIBeautyScoreHandler),
            (r"/roi_mark.html/?(.+)", AIBeautyScoreHandler),
            (r"/image/(.+)/(.+)", ImageHandler),
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
        conn.execute("""CREATE TABLE style_transfer (image_uuid char(36),
                                                     style_uuid char(36),
                                                     style TEXT,
                                                     image_style BLOB)
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


