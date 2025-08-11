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
""" Wrapper for Phaser js lib.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------
.. versionadded::    23.04
        try for an older brython version (06).

"""
from browser import window

GPHASER = window.Phaser
BG = None
try:
    from javascript import JSConstructor
    JSC = JSConstructor
    BG = JSConstructor(GPHASER.Game)
except ImportError:
    BG = GPHASER.Game.new


class JsPhaser(object):
    """
    Brython wrapper for Phaser.

    :return: Instance of JsPhaser.
    """
    _instance = None
    PHASER = GPHASER
    # JSC = JSConstructor
    BraserGame = BG
    # BraserGame = JSConstructor(PHASER.Game)

    def __new__(cls):

        if not cls._instance:
            cls._instance = super(JsPhaser, cls).__new__(cls)
        print("JsPhaser__new__")
        return cls._instance

    def phaser(self):
        """
        Javascript Phaser.

        :return: A Python reference for js Phaser.
        """
        return JsPhaser.PHASER

    def construct_(self, constructor):
        """
        Construct a Python version of a js Constructor.

        :param constructor: Js Constructor to be called.
        :return: The Python wrapper for the given js Constructor.
        """
        # return JsPhaser.JSC(constructor)
        return None


__all__ = ["core"]
from braser.core import Braser



