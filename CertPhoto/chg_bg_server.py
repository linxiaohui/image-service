# -*- coding: utf-8 -*-
import os
import hashlib
import base64
import uuid
from abc import ABC
from functools import wraps
import json
import sqlite3
import socket
import imghdr
import platform
if platform.system() == "Windows":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from chg_bg import change_background

class IndexHandler(tornado.web.RequestHandler, ABC):
    def get(self):
        self.render("index.html")

    def post(self):
        _conn = sqlite3.connect("image.db")
        file_metas = self.request.files.get('image_file', None)
        if not file_metas:
            self.render("index.html")
        else:
            for meta in file_metas:
                filename = meta['filename']
                data = meta['body']
                image_uuid = str(uuid.uuid4())
                _conn.execute("INSERT INTO upload_images (uuid, file_name, image_data) VALUES (?,?,?)",
                              (image_uuid, filename, data))
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
            content_type = imghdr.what(None, image[0])
            self.set_header("Content-Type", "image/"+content_type)
            self.write(image[0])
        else:
            self.set_status(404)

class ImageChangedHandler(tornado.web.RequestHandler, ABC):
    def get(self, gen_uuid):
        _conn = sqlite3.connect("image.db")
        _cursor = _conn.cursor()
        _cursor.execute("SELECT image_data FROM change_bg_color WHERE gen_uuid=?", (gen_uuid,))
        image = _cursor.fetchone()
        _conn.close()
        if image:
            content_type = imghdr.what(None, image[0])
            self.set_header("Content-Type", "image/"+content_type)
            self.write(image[0])
        else:
            self.set_status(404)

class ChangeBackgroundHander(tornado.web.RequestHandler, ABC):
    def post(self, image_uuid):
        _conn = sqlite3.connect("image.db")
        _cursor = _conn.cursor()
        _cursor.execute("SELECT image_data FROM upload_images WHERE uuid=?", (image_uuid,))
        image = _cursor.fetchone()
        if image:
            image_data = image[0]
            bg_color = self.get_argument("bg_color")
            _data = change_background(image_data, bg_color)[0]
            gen_uuid = str(uuid.uuid4())
            _cursor.execute("INSERT INTO change_bg_color(image_uuid, new_color, gen_uuid, image_data) VALUES (?,?,?,?)",
                            (image_uuid, bg_color, gen_uuid, _data))
            _conn.commit()
            _conn.close()
            self.redirect(f"/chg_bg/{gen_uuid}")
        else:
            _conn.close()
            self.set_status(404)
    
    def get(self, gen_uuid):
        self.render("image_chgbg.html", gen_uuid=gen_uuid)


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
            (r"/image_chg/(.+)", ImageChangedHandler),
            (r"/chg_bg/(.+)", ChangeBackgroundHander),
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
                                                   file_name TEXT, image_data BLOB, 
                                                   insert_time datetime default current_timestamp)
        """)
        conn.execute("""CREATE TABLE change_bg_color(image_uuid TEXT, new_color TEXT, gen_uuid TEXT,
                                                    image_data BLOB,
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
