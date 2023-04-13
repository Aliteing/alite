#! /usr/bin/env python
# -*- coding: UTF8 -*-
# Este arquivo é parte do programa Alite
# Copyright(c)2013 - 2014, Pedro Rodriguez <pedro.rodriguez.web @ gmail.com>
# All rights reserved.
# Copyright 2010–2022 Carlo Oliveira <carlo@nce.ufrj.br>,
# `Labase <http://labase.activufrj.nce.ufrj.br>`__; `GPL <http://j.mp/GNU_GPL3>`__.
#
# Alite é um software livre; você pode redistribuí-lo e/ou
# modificá-lo dentro dos termos da Licença Pública Geral GNU como
# publicada pela Fundação do Software Livre (FSF); na versão 3 da
# Licença.
#
# Este programa é distribuído na esperança de que possa ser útil,
# mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO
# a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, veja em <http://www.gnu.org/licenses/>
""" Game control server.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------
.. versionadded::    23.04
        open a user register window, receive score in json (06).

"""
import os
from typing import Optional, Awaitable

from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.ioloop import IOLoop
import json
# from model import DS


class LitHandler(RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass


class MainPage(LitHandler):

    def get(self):
        self.render("home.html", titulo="Alite - Games", version="23.04")


class Score(LitHandler):

    def get(self):
        import uuid
        session_id = str(uuid.uuid4().fields[-1])[:9]
        self.write(session_id)

    def post(self, *_):
        # fields = json.loads(self.request.body)
        # _fields = str(self.request.body, "utf8")
        data = json.loads(self.request.body.decode('utf-8'))
        print('Got JSON data:', data)
        # _fields = {k: v for pair in _fields.split('&') for k, v in pair.split("=") if pair}
        # _fields = dict([pair.split("=") for pair in _fields.split('&')])
        fields = self.request.body_arguments
        fields = {k: self.get_argument(k) for k in fields}
        # fields = {k: str(v[0], "utf8") for k, v in fields.items()}
        fields = json.dumps(fields)
        print("score post", fields, data, "*", _)


class Home(LitHandler):

    def get(self):
        import uuid
        session_id = str(uuid.uuid4().fields[-1])[:9]
        self.write(session_id)

    def post(self, *_):
        # fields = json.loads(self.request.body)
        fields = self.request.arguments
        fields = {k: str(v[0], "utf8") for k, v in fields.items()}
        fields = json.dumps(fields)
        print("home post", fields)
        self.render("game.html", titulo="Alite - Games", version="23.04")


def make_app():
    current_path = os.path.dirname(__file__)
    assets_path = os.path.join(current_path, "..", "game", "assets")
    static_path = os.path.join(current_path, "..", "game")
    template_path = os.path.join(current_path, "templates")
    image_path = os.path.join(current_path, "image")
    print(static_path)

    urls = [
        ("/", MainPage),
        ("/home/save", Home),
        ("/record/getid", Score),
        ("/record/store", Score),
        (r"/home/(.*\.py)", StaticFileHandler,  {'path': static_path}),
        (r"/home/assets/(.*\.png)", StaticFileHandler,  {'path': assets_path}),
        (r"/(.*\.css)", StaticFileHandler,  {'path': template_path}),
        (r"/image/(.*\.ico)", StaticFileHandler,  {'path': image_path}),
        (r"/image/(.*\.jpg)", StaticFileHandler,  {'path': image_path})
    ]
    return Application(
        urls, debug=True,
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=static_path
                       )


def start_server():
    from tornado.options import define, options

    define("port", default=8080, help="port to listen on for game server")
    app = make_app()
    app.listen(options.port)
    print(f"game listening on port {options.port}")
    IOLoop.instance().start()


if __name__ == '__main__':
    start_server()
