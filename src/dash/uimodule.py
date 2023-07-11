#! /usr/bin/env python
# -*- coding: UTF8 -*-
""" Módulos de interface html.


Classes neste módulo:
    - :py:class:`MenuEntry` Um item de menu .

Changelog
---------

.. versionadded::    23.07
    |br| add :class:`MenuEntry` (11),


|   **Open Source Notification:** This file is part of open source program **Alite**
|   **Copyright © 2023  Carlo Oliveira** <carlo@nce.ufrj.br>,
|   **SPDX-License-Identifier:** `GNU General Public License v3.0 or later <http://is.gd/3Udt>`_.
|   `Labase <http://labase.selfip.org/>`_ - `NCE <http://portal.nce.ufrj.br>`_ - `UFRJ <https://ufrj.br/>`_.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

"""
from tornado.web import UIModule
from dash import Configuration as Cfg
version__ = Cfg.version


# noinspection PyAttributeOutsideInit
class MenuEntry(UIModule):
    """ Classe antecessora dos requests.
    """

    def render(self, entry, show_comments=False):
        """ Inicializa os requests.

        Declara um conjunto de parâmetros iniciais da chamada base.

        :param     entry: O menu requisitado.
        :param      show_comments: Configuração para os chamados.
        """
        return self.render_string(
            "module-entry.html", entry=entry, show_comments=show_comments)

