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
""" General control server.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------
.. versionadded::    23.05
        Use namedtuple & dataclasses fon configuration (28)
        configure server=game db=GameDockerNoPass (28b)

"""
from collections import namedtuple
from dataclasses import dataclass, InitVar
import pathlib

from game_main import start_server as game_server
from tornado_main import start_server as kanban_server
from tornado.options import define, options

ServerKind = namedtuple("ServerKind", "game kanban")(0, 1)


@dataclass
class GameAtlasConfiguration:

    @staticmethod
    def get_pass():
        _path = pathlib.Path(__file__).parent.parent.parent / ".env"
        with open(_path, "r") as env:
            return env.read().split("=")[1].strip('"')

    passwd = get_pass()
    data_base = "alite_game",
    collection = "score",
    db_url = "alitelabase.b1lm6fr.mongodb.net"
    username = "carlotolla9"
    con_string = f"mongodb+srv://{username}:{passwd}@{db_url}/?retryWrites=true&w=majority"


@dataclass(frozen=True)
class GameDockerNoPasswordConfiguration:
    data_base: str = "alite_game",
    collection: str = "score",
    con_string: str = "mongodb://0.0.0.0:27017"
    config: InitVar[dict] = None

    def __post_init__(self, config: dict):
        if config:
            self.__init__(**config)

    # @staticmethod
    # def con_string():
    #     return GameDockerNoPasswordConfiguration._con_string

    # def __post_init__(self):
    #     object.__setattr__(self, '_con_string', cn)


@dataclass
class Configuration:
    version = "23.05"
    port = "8082"
    game = ServerKind.game
    kanban = ServerKind.kanban
    # db = GameAtlasConfiguration
    db = GameDockerNoPasswordConfiguration
    env = pathlib.Path(__file__).parent.parent.parent / ".env"


class Main:
    def __init__(self, config: ServerKind):
        self.config = config
        self.con_str = ""
        self.starter = {ServerKind.game: game_server, ServerKind.kanban: kanban_server}

    def start(self):
        self.starter[self.config]()

    def init(self):
        define("port", default=Configuration.port, help="port to listen on for game server")
        define("dbcon", default="mongodb://0.0.0.0:27017", help="connection string to database server")
        env = Configuration.env
        options.parse_config_file(env) if env else options.parse_command_line()
        con = options.dbcon
        print("GameDockerNoPasswordConfiguration.con_string = ", options.dbcon, con)
        GameDockerNoPasswordConfiguration(data_base="alite_game", collection="score", con_string=con)
        self.con_str = options.dbcon
        return self


if __name__ == '__main__':
    # Configuration.db._con_string = options.dbcon
    Main(Configuration.game).init().start()
