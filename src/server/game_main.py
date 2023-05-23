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
        select eica or wisconsin game, en exit (20).
        update score.put, mome.get and make_app (20a).
        add infra help, about, replay, restart menus (20b).

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


class Score(LitHandler):

    def post(self, **_):
        """Add a new game"""
        argument_dict = {k: self.get_argument(k) for k in self.request.arguments}
        # print("score post args", {x: self.get_argument(x) for x in self.request.arguments})
        # print(argument_dict)

        session_id = LitHandler.ds.add_game(**argument_dict)
        # session_id = LitHandler.ds.add_game(person=person, game=game, goal=goal_, trial=trial_)
        self.write(str(session_id))

    def put(self, **_):
        """Put a new score."""
        score = json.loads(self.request.body.decode('utf-8'))
        print("put data", score)
        game = score.pop("_id") if "_id" in score else score.pop("doc_id")
        session_id = LitHandler.ds.score(score_id=game, items=score)
        self.write(str(session_id))


class Home(LitHandler):

    def get(self):
        """Serves request games to select a game, or one of the games request: wsct, game"""
        import os.path as op
        page = self.request.uri
        print("page game", {x: self.get_argument(x) for x in self.request.arguments})
        person, _page, game_id = self.get_argument("oid", "101"), "home", "home"
        goal, trial = self.get_argument("goal", "0"), self.get_argument("trial", "0")
        if len(page) > 1:
            game_name = op.split(page)[-1].split("?")[0]  # recover the last path of the URI
            game_id = LitHandler.ds.add_game(person, game_name, goal=int(goal), trial=int(trial))
        self.render(f"{_page}.html", titulo="Alite - Games", version="23.05", session=game_id)

    def post(self, **_):
        """Add a new user."""
        # data = {k: v  for k, v in kw}
        data = {x: self.get_argument(x) for x in self.request.arguments}
        print("form data", data)
        # data = json.loads(data)
        # print('Got USER POST JSON data:', data)
        session_id = LitHandler.ds.insert(data)
        # self.write(str(session_id))
        self.render("games.html", titulo="Alite - Games", version="23.05", session=session_id)


def make_app(ds=None):
    from unittest.mock import MagicMock
    mds = MagicMock(name="mds")
    mds.insert.return_value = 100001
    mds.add_game.return_value = 300003
    LitHandler.ds = ds or mds
    current_path = os.path.dirname(__file__)
    assets_path = os.path.join(current_path, "..", "game", "assets")
    static_path = os.path.join(current_path, "..", "game")
    style_path = os.path.join(current_path, "css")
    infra_path = os.path.join(current_path, "infra")
    image_path = os.path.join(current_path, "image")
    # print(static_path)

    urls = [
        ("/", Home),
        ("/home/user", Home), ("/home/game", Home), ("/home/wcst", Home), ("/home/games", Home),
        (r"/record/oid", Score),
        ("/record/store", Score),
        (r"/infra/(.*\.html)", StaticFileHandler,  {'path': infra_path}),
        (r"/home/(.*\.py)", StaticFileHandler,  {'path': static_path}),
        (r"/home/assets/(.*\.png)", StaticFileHandler,  {'path': assets_path}),
        (r"/css/(.*\.css)", StaticFileHandler,  {'path': style_path}),
        (r"/image/(.*\.ico)", StaticFileHandler,  {'path': image_path}),
        (r"/image/(.*\.jpg)", StaticFileHandler,  {'path': image_path}),
        (r"/image/(.*\.png)", StaticFileHandler,  {'path': image_path})
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
