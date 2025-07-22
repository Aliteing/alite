#! /usr/bin/env python
# -*- coding: UTF8 -*-
"""Game model persistence as an abstract frame.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------

.. versionadded::    25.07
        initial version (21).

|   **Open Source Notification:** This file is part of open source program **Alite**
|   **Copyright © 2025  Carlo Oliveira** <carlo@nce.ufrj.br>,
|   **SPDX-License-Identifier:** `GNU General Public License v3.0 or later <http://is.gd/3Udt>`_.
|   `Labase <http://labase.activufrj.nce.ufrj.br/>`_ - `NCE <https://portal.nce.ufrj.br>`_ - `UFRJ <https://ufrj.br/>`_.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Dataclass:
    doc_id: str
    _id: Optional[int] = None

    def as_json_wo_none(self):
        return {key: value for key, value in asdict(self).items() if value is not None}

    def to_short_dict(self):
        result = asdict(self)
        result.pop('_id')
        return result


@dataclass
class Score(Dataclass):
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
class Trial(Dataclass):
    game_id = str = ""
    score: list[Score] = ()


@dataclass
class Goal(Dataclass):
    name: str = ""
    game_id = str = ""
    trial: list[Trial] = ()


@dataclass
class Game(Dataclass):
    game: str = ""
    player_id = str = ""
    goal: list[list[str]] = ()


@dataclass
class Player(Dataclass):
    name: str = ""
    school: str = ""
    year: int = 0
    age: int = 0
    sex: str = ""
    private: bool = False
    begin: datetime = ""
    end: datetime = ""
    games: list[Game] = ()


@dataclass
class Team(Dataclass):
    name: str = ""
    players: list[Player] = ()
