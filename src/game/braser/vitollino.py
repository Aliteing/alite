#! /usr/bin/env python
# -*- coding: UTF8 -*-
# Este arquivo é parte do programa EICA
# Copyright 2014-2017 Carlo Oliveira <carlo@nce.ufrj.br>,
# `Labase <http://labase.selfip.org/>`__; `GPL <http://j.mp/GNU_GPL3>`__.
#
# EICA é um software livre; você pode redistribuí-lo e/ou
# modificá-lo dentro dos termos da Licença Pública Geral GNU como
# publicada pela Fundação do Software Livre (FSF); na versão 2 da
# Licença.
#
# Este programa é distribuído na esperança de que possa ser útil,
# mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO
# a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, veja em <http://www.gnu.org/licenses/>

"""Encapsulate javascript library Phaser.

.. moduleauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------
.. versionadded::    23.05
        change Phaser div id to pydiv, change POST to PUT (20).

"""
from braser import Braser
from browser import doc


class Vitollino:
    _instance = None
    BRASER = None
    GID = "00000000000000000000"

    def __init__(self, w=800, h=800, mode=None, name="pydiv", states=None, alpha=False):
        self._init(w, h, mode, name, states, alpha)
        self.gamer = Vitollino.BRASER
        self.gamer.subscribe(self)
        self.game = self.gamer.game
        self.gid = "00000000000000000000"

    def registry(self, *args, **kwargs):
        pass

    def set_id(self, gid):
        Vitollino.GID = gid
        print(gid)

    def _init(self, w=800, h=800, mode=None, name="pydiv", states=None, alpha=False):
        doc["pydiv"].html = ""
        Vitollino.BRASER = Braser(w, h, mode, name, states, alpha)
        # Vitollino.BRASER.send('getid', {}, self.set_id, "GET")

    def preload(self):
        pass

    def create(self):
        pass

    def spritesheet(self, name, img, x=0, y=0, s=1):
        self.game.load.spritesheet(name, img, x, y, s)

    def group(self):
        return self.game.add.group()

    def tween(self, sprite, time, function="Linear", autostart=True, delay=0, repeat=-1, yoyo=False, **kwd):
        return self.game.add.tween(sprite).to(dict(kwd), time, function, autostart, delay, repeat, yoyo)

    def enable(self, item):
        self.game.physics.arcade.enable(item)

    def start_system(self):
        self.game.physics.startSystem(self.gamer.PHASER.Physics.ARCADE)

    def image(self, name, img):
        return self.game.load.image(name, img)

    def sprite(self, name, x=0, y=0):
        return self.game.add.sprite(x, y, name)

    def update(self):
        pass

    def score(self, evento, carta, ponto, valor):
        carta = '_'.join(carta)
        casa = '_'.join([str(evento.x), str(evento.y)])
        data = dict(doc_id=Vitollino.GID, carta=carta, casa=casa, move="ok", ponto=ponto, valor=valor)
        self.gamer.send('store', data, method="PUT")
        print('store', data)

    def register(self, evento, carta, ponto, valor):
        carta = '_'.join(carta)
        data = dict(doc_id=Vitollino.GID, carta=carta, casa=evento, move="ok", ponto=ponto, valor=valor)
        self.registry(evento, carta, ponto)


class Actor(Vitollino):
    def _init(self, w=800, h=800, mode=None, name="braser", states=None, alpha=False):
        pass
