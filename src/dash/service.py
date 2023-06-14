#! /usr/bin/env python
# -*- coding: UTF8 -*-
""" Ponto de entrada do dashboard service.

Classes neste módulo:
    - :py:class:`DashService` Serviços de plotagem dos dados de Alite-Games.
    - :py:meth:`DashService.plot_pontos` Plota o número de jogos executados no Alite-games e retorna um plot.

Changelog
---------
.. versionadded::    23.06
    |br| first version of main (09)
    |br| added person pontos (09)
    |br| added more documentation (14)

|   **Open Source Notification:** This file is part of open source program **Alite**
|   **Copyright © 2023  Carlo Oliveira** <carlo@nce.ufrj.br>,
|   **SPDX-License-Identifier:** `GNU General Public License v3.0 or later <https://is.gd/3Udt>`_.
|   `Labase <http://labase.selfip.org/>`_ - `NCE <http://portal.nce.ufrj.br>`_ - `UFRJ <https://ufrj.br/>`_.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

"""
from nameko.rpc import rpc
from pandas import DataFrame
from dash import Configuration as Cfg


class DashService:
    """ Serviços de plotagem dos dados de Alite-Games.

    """
    name = Cfg.dash_srv

    def __init__(self):
        self.person_url = Cfg.person_url
        self.df: DataFrame = DataFrame()

    def person_load(self, person=Cfg.person_url):
        """ Carrega as informações de dados a partir de um servidor num arcabouço.

        :param person: Url que endereça os dados necessários
        :return: None
        """
        import urllib.request
        import json
        import pandas as pd
        with urllib.request.urlopen(person) as url:
            data = json.loads(url.read().decode())
            self.df = pd.DataFrame(data)
        self.df['games_l'] = [[g["game"] for g in t] for t in self.df.games]

    @rpc
    def plot_pontos(self):
        """ Plota o número de jogos executados no Alite-games.

        :return: O gráfico plotado em forma se sequência codificada em base64
        """
        import seaborn as sns
        from matplotlib import pyplot as plt
        self.person_load()
        dfx = self.df.explode('games_l')
        _ = plt.figure(figsize=(15, 8))
        chart = sns.countplot(data=dfx, x="name", hue="games_l")
        _ = chart.set(title='Contagem dos Jogos', ylabel='Número de Jogos', xlabel="Participantes")
        _ = chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment='right')
        from io import BytesIO
        img = BytesIO()
        plt.savefig(img, format='png')
        plt.close()
        img.seek(0)
        import base64
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        return plot_url
