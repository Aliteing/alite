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
        send score in json (06).

"""
from braser import JsPhaser
from browser.ajax import ajax


class Braser:
    """
    Brython object-oriented  wrapper for js Phaser.

    :param x: Canvas width.
    :param y: Canvas height.
    :param mode: Canvas mode.
    :param name: Game name.
    :param keyargs: Extra arguments
    """
    PHASER = JsPhaser().phaser()
    AUTO = JsPhaser().phaser().AUTO
    CANVAS = JsPhaser().phaser().CANVAS
    Game = JsPhaser().BraserGame

    def __init__(self, x=800, y=600, mode=None, name="braser", states=None, alpha=False, **_):
        mode = mode or Braser.CANVAS
        states = {"preload": self.preload, "create": self.create, "update": self.update} if states is None else states
        self.game = Braser.Game(x, y, mode, name, states, alpha)
        self.subscribers = []

    def subscribe(self, subscriber):
        """
        Subscribe elements for game loop.

        :param subscriber:
        """
        self.subscribers.append(subscriber)

    def preload(self, *_):
        """
        Preload element.

        """
        for subscriber in self.subscribers:
            subscriber.preload()

    def create(self, *_):
        """
        Create element.

        """
        for subscriber in self.subscribers:
            subscriber.create()

    def update(self, *_):
        """
        Update element.

        """
        for subscriber in self.subscribers:
            subscriber.update()

    def send(self, operation, data, action=lambda t: None, method="POST"):
        def on_complete(request):
            if int(request.status) == 200 or request.status == 0:
                # print("req = ajax()== 200", request.text)
                action(request.text)
            else:
                print("error " + request.text)

        req = ajax()
        req.bind('complete', on_complete)
        # req.on_complete = on_complete
        url = "/record/" + operation
        req.open(method, url, True)
        # req.set_header('content-type', 'application/x-www-form-urlencoded')
        req.set_header("content-type", "application/json")
        # req.set_header("Content-Type", "application/json; charset=utf-8")
        import json
        data = json.dumps(data)
        print("def send", data)
        req.send(data)
