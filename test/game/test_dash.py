#! /usr/bin/env python
# -*- coding: UTF8 -*-
""" Teste do dashboard service e do servidor.

Classes neste módulo:
    - :py:class:`TestDashService` Testa Serviços de plotagem dos dados de Alite-Games.
    - :py:class:`TestDashHandler` Testa Servidor de plotagem dos dados de Alite-Games.

Changelog
---------
.. versionadded::    23.06
    |br| added TestDashService (20)
    |br| added TestDashHandler (20)
    |br| test all plotting services (21)

|   **Open Source Notification:** This file is part of open source program **Alite**
|   **Copyright © 2023  Carlo Oliveira** <carlo@nce.ufrj.br>,
|   **SPDX-License-Identifier:** `GNU General Public License v3.0 or later <https://is.gd/3Udt>`_.
|   `Labase <http://labase.selfip.org/>`_ - `NCE <http://portal.nce.ufrj.br>`_ - `UFRJ <https://ufrj.br/>`_.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

"""
import unittest
from tornado.testing import AsyncHTTPTestCase
from unittest.mock import MagicMock, patch
from dash.server import make_server_app
from dash import Configuration as Cfg
from dash.service import DashService, WiscPlot
from pandas import DataFrame

MOCK_PRX1 = MagicMock(name="cluster_rpc")
MOCK_PANDA = MagicMock(name="pandas_df")
MOCK_URL = MagicMock(name="mock_url")


class TestDashService(unittest.TestCase):
    @patch('urllib.request.urlopen', MagicMock(name="nameko_rpc"))
    def setUp(self):
        def set_dash_df(*_):
            self.dash.wisc_plot.df = DataFrame.from_dict(dict(_id=['456'], ponto=['000'], valor=['0000']))
            return DataFrame.from_dict(dict(_id=['456'], name=['000'], valor=['0000']))
        self.mock_url = MagicMock(spec="XXXXXXX@@@@@@@@mock_urlXXXXXX")
        self.mock_df = MagicMock(spec="XXXXXXX@@@@@@@@mock_dfXXXXXX")
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.return_value = self.mock_url
        self.dash = DashService()
        self.dash.person_load = self.mock_url
        self.dash.wisc_plot.get_all_games = self.mock_df
        self.dash.wisc_plot.refine_point_value_info = self.mock_df
        self.mock_df.return_value = DataFrame.from_dict(dict(_id=["'456'"], name=['000'], valor=['0000']))
        self.mock_df.side_effect = set_dash_df
        self.mock_url.return_value = [dict(_id="'123'")]

    @patch('pandas.DataFrame', MOCK_PANDA)
    def test_create(self):
        service = self.dash
        self.assertIsInstance(service.wisc_plot, WiscPlot, "failed to create WiscPlot")
        self.assertIsInstance(service.df, DataFrame, "failed  to create DataFrame")

    @patch('pandas.DataFrame', MagicMock(name="pd_dataframe"))
    def test_plot_chart(self):
        plot_kind = "countplot catplot violinplot histplot heatmap".split()

        plot = {k: v for k, v in zip(Cfg.plot_kind, plot_kind)}
        with patch('pandas.melt', create=True) as mock_pandas:
            mock_pandas.__enter__.return_value = MOCK_URL  # self.mock_url
            # MOCK_URL.read.decode.return_value = b""
            plot.pop("factor")
            for kind, function in plot.items():
                with patch(f'seaborn.{plot[kind]}'):
                    data = self.dash.plot_chart(kind)
                    # print(mock_seaborne, mock_seaborne.__enter__)
                    self.assertLess(1000, len(data), "failed retrieve main")


class TestDashHandler(AsyncHTTPTestCase):
    @patch('nameko.rpc.RpcProxy', MagicMock(name="nameko_rpc"))
    def get_app(self):
        with patch('nameko.standalone.rpc.ClusterRpcProxy') as mock_cluster:
            mock_cluster.return_value = MagicMock(spec="XXXXXXX@@@@@@@@XXXXXX")
        # self.db = Facade(db=collection)
        return make_server_app(config=Cfg.dash_srv, debug=False)[1]

    def test_homepage(self):
        response = self.fetch("/")
        self.assertEqual(200, response.code, "failed retrieve main")
        self.assertIn(b"Alite - Dashboard", response.body)

    @patch('nameko.standalone.rpc.ClusterRpcProxy', MOCK_PRX1)
    def test_get_point(self):
        MOCK_PRX1.__enter__.return_value = MagicMock(name="prx0XXXXXXXXX")
        response = self.fetch("/chart/")
        self.assertEqual(200, response.code, "failed retrieve main")
        self.assertIn(b"__enter__().datascience_dash_service.plot_pontos()", response.body)

    @patch('nameko.standalone.rpc.ClusterRpcProxy', MOCK_PRX1)
    def test_get_chart(self):
        # MOCK_PRX1.__enter__.return_value = MagicMock(name="prx0XXXXXXXXX")
        response = self.fetch("/chart/heat")
        self.assertEqual(200, response.code, "failed retrieve main")
        self.assertIn(b"__enter__().datascience_dash_service.plot_chart()", response.body)


if __name__ == '__main__':
    unittest.main()
