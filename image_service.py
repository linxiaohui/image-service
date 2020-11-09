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

from u2net_rpc import U2NetCutOut
PREDICTOR = U2NetCutOut()

class IndexHandler(tornado.web.RequestHandler, ABC):
    def get(self):
        self.render("index.html")
    def post(self):
        _conn = sqlite3.connect("image.db")
        url = self.get_argument("image_url", None)
        if not url:
            self.render("index.html")
        else:
            resp = requests.get(url)
            data = resp.content
            _data = PREDICTOR.cutout(data)[0]
            image_uuid = str(uuid.uuid4())
            _conn.execute("INSERT INTO upload_images (uuid, file_name, image_data, image_fg) VALUES (?,?,?,?)",
                          (image_uuid, url, data, _data))
            _conn.commit()
        _conn.close()
        self.render("image.html", image_uuid=image_uuid)

class ImageHandler(tornado.web.RequestHandler, ABC):
    def get(self, image_uuid):
        _conn = sqlite3.connect("image.db")
        _cursor = _conn.cursor()
        _cursor.execute("SELECT image_data FROM upload_images WHERE uuid=?", (image_uuid,))
        image = _cursor.fetchone()
        _conn.close()
        if image:
            self.write(image[0])
        else:
            self.set_status(404)

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
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "."),
            xsrf_cookies=False,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            autoescape=None,
        )
        handlers = [
            (r"/", IndexHandler),
            (r"/image/(.+)", ImageHandler),
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
        conn = sqlite3.connect("image.db")
        conn.execute("""CREATE TABLE upload_images(image_id INTEGER PRIMARY KEY AUTOINCREMENT, uuid TEXT, 
                                                   file_name TEXT, image_data BLOB, image_fg BLOB,
                                                   insert_time datetime default current_timestamp)
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


