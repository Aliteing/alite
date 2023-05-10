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
.. versionadded::    23.05
        use ds for web requests, migrate Main to Home (10).

.. versionadded::    23.04
        open a user register window, receive score in json (06).
        reroute restore/game id to restore/oid (20).

"""
import os
from typing import Optional, Awaitable

from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.ioloop import IOLoop
import json
# from model import DS


class LitHandler(RequestHandler):
    ds = None
    """Just implements abstract data_received"""
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass


class MainPage(LitHandler):

    def get(self):
        self.render("home.html", titulo="Alite - Games", version="23.05")

    def post(self, **_):
        data = json.loads(self.request.body.decode('utf-8'))
        print('Got USER POST JSON data:', data)
        fields = self.request.body_arguments
        fields = {k: self.get_argument(k) for k in fields}
        fields_ = json.dumps(fields)
        print("user post", fields_, data, "*", _)
        session_id = LitHandler.ds.insert(fields)
        self.write(str(session_id))


class Score(LitHandler):

    def get(self):
        import uuid
        session_id = str(uuid.uuid4().fields[-1])[:9]
        self.write(session_id)

    def post(self, **_):
        """Add a new game"""
        data = json.loads(self.request.body.decode('utf-8'))
        person, game = data['person'], data['game']
        # print('Got POST JSON data:', data, person, game)
        session_id = LitHandler.ds.add_game(person=person, game=game)
        self.write(str(session_id))

    def put(self, **_):
        """Put a new score."""
        data = json.loads(self.request.body.decode('utf-8'))
        game, score = data['game'], data['score']
        # print('Got PUT JSON data:', data)
        session_id = LitHandler.ds.score(score_id=game, items=score)
        self.write(str(session_id))


class Home(LitHandler):

    def get(self):
        self.render("home.html", titulo="Alite - Games", version="23.05")

    def post(self, **_):
        """Add a new user."""
        data = json.loads(self.request.body.decode('utf-8'))
        # print('Got USER POST JSON data:', data)
        session_id = LitHandler.ds.insert(data)
        self.write(str(session_id))


def make_app(ds=None):
    LitHandler.ds = ds
    current_path = os.path.dirname(__file__)
    assets_path = os.path.join(current_path, "..", "game", "assets")
    static_path = os.path.join(current_path, "..", "game")
    template_path = os.path.join(current_path, "templates")
    image_path = os.path.join(current_path, "image")
    # print(static_path)

    urls = [
        ("/", Home),
        ("/home/user", Home),
        (r"/record/oid", Score),
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
