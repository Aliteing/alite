#! /usr/bin/env python
# -*- coding: UTF8 -*-
""" Inicialização geral do módulo dash

Changelog
---------
.. versionadded::    23.06
   |br| new plotting url at :class:`Configuration` (10)
   |br| plotting kind at :class:`Configuration` (21)
   |br| GET_DASH & PLOT_TPL at :class:`Configuration` (23)

|   **Open Source Notification:** This file is part of open source program **Alite**
|   **Copyright © 2023  Carlo Oliveira** <carlo@nce.ufrj.br>,
|   **SPDX-License-Identifier:** `GNU General Public License v3.0 or later <http://is.gd/3Udt>`_.
|   `Labase <http://labase.selfip.org/>`_ - `NCE <http://portal.nce.ufrj.br>`_ - `UFRJ <https://ufrj.br/>`_.

"""
__version__ = "23.06"
from collections import namedtuple
from dataclasses import dataclass
import pathlib
ServerKind = namedtuple("ServerKind", "web rpc")(0, 1)


@dataclass
class MongoConfiguration:

    @staticmethod
    def get_pass():
        _path = pathlib.Path(__file__).parent.parent.parent / ".env"
        with open(_path, "r") as dot_env:
            _env = dot_env.read().split("\n")
            import re
            _env = [re.findall(r'(.+?)="(.+?)"', line)[0] for line in _env if line]
            _env = {k: v for k, v in _env}
            return _env

    ev = get_pass()
    passwd = ev['MONGO_PASS']
    data_base = "alite_game",
    collection = "score",
    db_url = ev["dbcon"]
    atlas_url = ev["atlas"]
    username = "carlotolla9"
    con_string = f"mongodb+srv://{username}:{passwd}@{db_url}/?retryWrites=true&w=majority"


@dataclass
class Configuration:
    version = __version__
    port = "8082"
    web = ServerKind.web
    rpc = ServerKind.rpc
    current = rpc
    db = MongoConfiguration
    env = pathlib.Path(__file__).parent.parent.parent / ".env"
    tpl = pathlib.Path(__file__).parent / "tpl"
    img = pathlib.Path(__file__).parent / "image"
    css = pathlib.Path(__file__).parent / "css"
    person_url = 'https://games.alite.selfip.org/score/players'
    game_url = 'https://games.alite.selfip.org/score/games?oid={}'
    plot_kind = "plot factor violin hist heat".split()
    dash_srv = "datascience_dash_service"
    STT_PATH = r"/image/(.*)"
    CSS_PATH = r"/css/(.*\.css)"
    GET_DASH = r'/dash/?(.?)'
    GET_POINT = r'/chart/?(.?)'
    # GET_GAMES = r'/chart/(?P<id>[a-zA-Z0-9-]+)/?'
    GET_GAMES = r'/chart/(?P<pid>[a-zA-Z0-9-]+)/?'
    ERR_TPL = "erro404.html"
    DASH_TPL = "dash.html"
    PLOT_TPL = "plot.html"
    BOIL_TPL = "boiler.html"
    AMQP_URI = "amqp://guest:guest@127.0.0.1:5672"
    config = {'AMQP_URI': AMQP_URI}
    debug = False
    service = None
