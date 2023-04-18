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
"""Game model persistence as an abstract frame.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------

.. versionadded::    23.04
        initial version (13).
        nested architecture (18).

"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class MongoDataclass:
    doc_id: str
    _id: Optional[int] = None

    def as_json_wo_none(self):
        return {key: value for key, value in asdict(self).items() if value is not None}

    def to_short_dict(self):
        result = asdict(self)
        result.pop('_id')
        return result


@dataclass
class Score(MongoDataclass):
    trial_id: int = 0
    marker: str = 0
    slot: str = ""
    move: str = ""
    location: tuple = (0, 0)
    state: str = ""
    score: float = 0.0
    time: datetime = ""
    result: str = ""


@dataclass
class Trial(MongoDataclass):
    name: str = ""
    goal_id = str = ""
    score: list[Score] = ()


@dataclass
class Goal(MongoDataclass):
    name: str = ""
    game_id = str = ""
    trial: list[Trial] = ()


@dataclass
class Game(MongoDataclass):
    game: str = ""
    player_id = str = ""
    goal: list[Goal] = ()


@dataclass
class Registry(MongoDataclass):
    name: str = ""
    school: str = ""
    year: int = 0
    age: int = 0
    sex: str = ""
    private: bool = False
    begin: datetime = ""
    end: datetime = ""
    games: list[Game] = ()
