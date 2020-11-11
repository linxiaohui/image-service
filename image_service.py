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
    def get(self):
        self.render("index.html")

class AIBeautyScoreHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid):
        self.render("beauty_score.html")
    

class ImageForegroundHandler(tornado.web.RequestHandler, ABC):
    def get(self, gen_uuid):
        _conn = sqlite3.connect("image.db")
        _cursor = _conn.cursor()
        _cursor.execute("SELECT image_fg FROM  upload_images WHERE uuid=?", (gen_uuid,))
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
            (r"/beauty_score/?(.+)", AIBeautyScoreHandler),
            (r"/cartoon/?(.+)", AIBeautyScoreHandler),
            (r"/face_cartoon/?(.+)", AIBeautyScoreHandler),
            (r"/face_sketch/?(.+)", AIBeautyScoreHandler),
            (r"/style_transfer/?(.+)", AIBeautyScoreHandler),
            (r"/fore_ground/?(.+)", AIBeautyScoreHandler),
            (r"/cert_photo/?(.+)", AIBeautyScoreHandler),
            (r"/mosaic_app/?(.+)", AIBeautyScoreHandler),
            (r"/nsfw_mosaic/?(.+)", AIBeautyScoreHandler),
            (r"/roi_mosaic/?(.+)", AIBeautyScoreHandler),
            (r"/nsfw/?(.+)", AIBeautyScoreHandler),
            (r"/roi_mark/?(.+)", AIBeautyScoreHandler),
            (r"/image_fg/(.+)", ImageForegroundHandler),
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
        conn = get_db_conn()
        conn.execute("""CREATE TABLE input_image (image_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                                  image_uuid TEXT, 
                                                  file_name TEXT,
                                                  image_data BLOB,
                                                  params TEXT,
                                                  insert_time datetime default current_timestamp)
        """)
        conn.create("""CREATE TABLE beauty_score(image_id INT,
                                                 image_landmark BLOB, 
                                                 image_rect BLOB,
                                                 face_rank float,
                                                 beauty_predict float,
                                                 baidu_score float,
                                                 facepp_score float)
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


