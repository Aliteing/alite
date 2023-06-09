#! /usr/bin/env python
# -*- coding: UTF8 -*-
""" Ponto de entrada do módulo dash.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------
.. versionadded::    23.06
        first version of main (09)

    This file is part of  program Alite
    Copyright © 2023  Carlo Oliveira <carlo@nce.ufrj.br>,
    `Labase <http://labase.selfip.org/>`_ - `NCE <http://portal.nce.ufrj.br>`_ - `UFRJ <https://ufrj.br/>`_.
    SPDX-License-Identifier: `GNU General Public License v3.0 or later <http://is.gd/3Udt>`_.

"""
from dash import Configuration as Cfg
from dash.service import DashService


class Main:
    def __init__(self):
        self.run = [self.web, self.rpc_srv][Cfg.current]

    def web(self):
        ...

    def rpc_srv(self):
        # from dash.service import DashService
        # from nameko.containers import ServiceContainer
        # container = ServiceContainer(DashService, config=dict(AMQP_URI='pyamqp://guest:guest:15672@rabbitmq'))
        # ``container.extensions`` exposes all extensions used by the service
        # start service
        # container.start()
        _ = DashService()
        print("Main - GreetingService")

    def runner(self):
        self.run()


Main().runner()


if __name__ == '__main__':
    ...

