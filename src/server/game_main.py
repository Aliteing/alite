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
        fix home get to deal correctly all pages (24).
        add game_id to page template, extract make_mock (25).
        recover home get from pager trials (25b).
        add timestamp with Rio timezone (28)
        add score retrieval for players & games (29)
        erro 404, conserta score/games|game (30)

.. versionadded::    23.04
        open a user register window, receive score in json (06).
        reroute restore/game id to restore/oid (20).

"""
import os
from typing import Optional, Awaitable

from bson.objectid import ObjectId
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.ioloop import IOLoop
import json

import model.game_facade


# from model import DS


class LitHandler(RequestHandler):
    ds: model.game_facade.Facade
    """Just implements abstract data_received"""

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass


class DefaultHandler(RequestHandler):
    def prepare(self):
        # Use prepare() to handle all the HTTP methods
        self.set_status(404)
        self.render("erro404.html", titulo="Alite - Erro 404", version="23.05")

        # self.finish("404 - my thing")


class JSONSerializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return obj.__repr__()

        return json.JSONEncoder.default(self, obj)


class Score(LitHandler):

    def get(self):
        """Recover data from database"""

        def players():
            play = LitHandler.ds.load_all()
            return play

        def player():
            return LitHandler.ds.load_player(oid=person)

        def games():
            return LitHandler.ds.expand_item(oid=person)

        def game():
            return LitHandler.ds.load_item(dict(_id=person))

        import os.path as op
        page = self.request.uri
        person = self.get_argument("oid", "0")
        # person, goal, trial = [self.get_argument(arg, "0") for arg in "oid goal trial".split()]
        game_name = op.split(page)[-1].split("?")[0] or "home"  # recover the last path of the URI
        functions = zip("players player games game".split(), [players, player, games, game])

        pager = {path: function for path, function in functions}
        # print("game_id, trial_", game_name, pager[game_name], pager[game_name]())
        # print("page game", {x: self.get_argument(x) for x in self.request.arguments})
        data = pager[game_name]()
        self.set_header('Content-Type', 'application/json')
        # self.write(json.dumps(json.loads(json.dumps(data, cls=JSONSerializer))))
        self.write(json.dumps(data, cls=JSONSerializer))

        # self.write(data)

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
        # print("put score data", score)
        game = score.pop("_id") if "_id" in score else score.pop("doc_id")
        session_id = LitHandler.ds.score(score_id=game, items=score)
        self.write(str(session_id))


class Home(LitHandler):

    def get(self):
        """Serves request games to select a game, or one of the games request: wsct, game"""

        def games():
            return person, 0

        def gamer():
            game_id, trial_ = LitHandler.ds.add_game(person, game_name, goal=int(goal), trial=int(trial))
            return game_id, trial_

        import os.path as op
        page = self.request.uri
        person, goal, trial = [self.get_argument(arg, "0") for arg in "oid goal trial".split()]
        game_name = op.split(page)[-1].split("?")[0] or "home"  # recover the last path of the URI

        pager = {path: function for path, function in zip("games home wcst game".split(), [games, games, gamer, gamer])}
        # print("game_id, trial_", game_name, pager[game_name], pager[game_name]())
        # print("page game", {x: self.get_argument(x) for x in self.request.arguments})
        _game_id, _trial = pager[game_name]()

        self.render(f"{game_name}.html", titulo="Alite - Games", version="23.05",
                    session=person, game_id=_game_id, goal=goal, trial=_trial)

    def post(self, **_):
        """Add a new user."""
        # data = {k: v  for k, v in kw}
        data = {x: self.get_argument(x) for x in self.request.arguments}
        from datetime import datetime, timezone, timedelta
        timezone_info = timezone(timedelta(hours=-3.0))
        data.update(dict(time=str(datetime.now(timezone_info))))
        session_id = LitHandler.ds.insert(data)
        self.render("games.html", titulo="Alite - Games", version="23.05", session=session_id)


def make_mock():
    from unittest.mock import MagicMock
    mds = MagicMock(name="mds")
    mds.insert.return_value = 100001
    mds.add_game.return_value = 300003, 0
    mds.add_trial.return_value = 400003, 1
    return mds


def make_app(ds=None):
    LitHandler.ds = ds or make_mock()
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
        ("/score/player", Score), ("/score/players", Score), ("/score/games", Score), ("/score/game", Score),
        (r"/infra/(.*\.html)", StaticFileHandler, {'path': infra_path}),
        (r"/home/(.*\.py)", StaticFileHandler, {'path': static_path}),
        (r"/home/assets/(.*\.png)", StaticFileHandler, {'path': assets_path}),
        (r"/css/(.*\.css)", StaticFileHandler, {'path': style_path}),
        (r"/image/(.*\.ico)", StaticFileHandler, {'path': image_path}),
        (r"/image/(.*\.jpg)", StaticFileHandler, {'path': image_path}),
        (r"/image/(.*\.png)", StaticFileHandler, {'path': image_path})
    ]
    return Application(
        urls, debug=True,
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=static_path,
        default_handler_class=DefaultHandler
    )


def start_server():
    from tornado.options import options
    from model.game_facade import Facade
    app = make_app(Facade())
    app.listen(options.port)
    print(f"game listening on port {options.port}")
    IOLoop.instance().start()


if __name__ == '__main__':
    start_server()
