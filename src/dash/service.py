#! /usr/bin/env python
# -*- coding: UTF8 -*-
""" Ponto de entrada do dashboard service.

Classes neste módulo:
    - :py:class:`DashService` Serviços de plotagem dos dados de Alite-Games.
    - :py:meth:`DashService.plot_pontos` Plota o número de jogos executados no Alite-games e retorna um plot.

Changelog
---------
.. versionadded::    23.07
    |br| added player time chart (04)

.. versionadded::    23.06
    |br| first version of main (09)
    |br| added person pontos (09)
    |br| added more documentation (14)
    |br| added plotting class draft (19)
    |br| added initial templating method, include value plot (21)
    |br| fix Pnt & joiner; added x-lim & y-lim to plots (30)

|   **Open Source Notification:** This file is part of open source program **Alite**
|   **Copyright © 2023  Carlo Oliveira** <carlo@nce.ufrj.br>,
|   **SPDX-License-Identifier:** `GNU General Public License v3.0 or later <https://is.gd/3Udt>`_.
|   `Labase <http://labase.selfip.org/>`_ - `NCE <http://portal.nce.ufrj.br>`_ - `UFRJ <https://ufrj.br/>`_.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

"""
import json
import urllib.request
from collections import namedtuple
import seaborn as sns
from matplotlib import pyplot as plt
from pandas import DataFrame
import pandas as pd
import numpy as np
from dash import Configuration as Cfg
from nameko.rpc import rpc


class WiscPlot:
    """ Internal service to plot a number of charts.

    """
    Cfplot = namedtuple("Cfplot", "col title ylabel xlabel")
    """ Plotting configuration.

    .. py:attribute:: col

        Column of dataframe

    .. py:attribute:: title

        Title of the plot figure

    .. py:attribute:: ylabel

        Label to describe the Y axis

    .. py:attribute:: xlabel

        Label to describe the X axis

    """

    Pnt = namedtuple("Pnt", "ok no td")
    """ Point column description.

    .. py:attribute:: ok

        Number of current correct answers

    .. py:attribute:: no

        Number of current wrong answers

    .. py:attribute:: td

        Number of current all no matching answers

    """
    Val = namedtuple("Val", "cc cf cn ct")
    """ Value column description.

    .. py:attribute:: cc

        Matches current color

    .. py:attribute:: cf

        Matches current shape

    .. py:attribute:: cn

        Matches current number

    .. py:attribute:: ct

        Current chosen property 0-color, 1-shape, 2-number

    """

    def __init__(self, game_url='https://games.alite.selfip.org/score/games?oid={}'):
        self.game_url = game_url
        self.df: DataFrame = DataFrame()
        self.game_data = []
        self.count = 0

    def retrieve_games(self, player):
        """ Retrieve from remote source data for a given player

        :param player: Given player id; identification
        :return: None
        """
        with urllib.request.urlopen(self.game_url.format(player)) as urlp:
            self.game_data.extend(json.loads(urlp.read().decode()))

    def process_df(self):
        """ Shapes current dataframe to filter wisc and replace the column scorer

        :return:
        """
        dfg_ = DataFrame(self.game_data)
        dfg_ = dfg_.loc[dfg_['game'] == 'wcst']
        dfx_ = dfg_.explode('scorer')
        dfl_ = DataFrame(dfx_.scorer.values.tolist())
        dfx_ = dfx_.drop(columns=["scorer"], inplace=False).reset_index()
        return dfx_.join(dfl_)

    def get_all_games(self, player_oids):
        """ Get all games from a given player.

        :param player_oids: Given player id
        :return: None (assign to current df attribute)
        """
        _ = [self.retrieve_games(oid) for oid in player_oids]
        # print(self.game_data)
        self.df = self.process_df()

    def retrieve_oid_from_person_df(self, person_df):
        """ Trim id vale from extra surroundings.

        :param person_df: Given player dataframe
        :return: self (this object)
        """
        import re
        # noinspection PyProtectedMember
        oid_list = [re.findall(r"'(.+?)'", text)[0] for text in person_df._id.to_list()]
        self.get_all_games(oid_list)
        return self

    def refine_point_value_info(self):
        """ Extract some cognitive relevant properties from existing data,

        :return: transformed dataframe with new columns
        """

        def counter(a, b):
            """ Counts repetition of a figure.

            :param a: current figure of the series
            :param b: next figure of the series
            :return: count if prevails or zero if not
            """
            a, b = int(a), int(b)
            self.count += (1 if a else 0)
            count, self.count = self.count if not b else 0, 0 if not b else self.count
            return count

        def joiner(k, t, w):
            k, t = int(k), int(t)
            return int(int(t != w) * 2 ** w * k)

        def bother(c, f, n, t):
            c, f, n, t = int(c), int(f), int(n), int(t) % 3
            all_k = [c, f, n]
            if t > 2 or t < 0:
                raise ValueError(t)
            target = all_k.pop(t)
            return target * sum(all_k)

        point_list = [self.Pnt(text[:-2], *list(text[-2:])) for text in self.df.ponto.to_list()]
        new_list = point_list[1:] + [self.Pnt(0, 0, 0)]
        val_list0 = [self.Val(*list(text)) for text in self.df.valor.to_list()]
        val_list = [joiner(val.cc, val.ct, 0) + joiner(val.cf, val.ct, 1) + joiner(val.cn, val.ct, 2)
                    for val in
                    val_list0]
        val_list1 = val_list[1:] + [0]
        conservation = [counter(a.ok, b.ok) for a, b in zip(point_list, new_list)]
        perseveration = [counter(a.no, b.no) for a, b in zip(point_list, new_list)]
        oposition = [counter(a.td, b.td) for a, b in zip(point_list, new_list)]
        deviation = [counter(a, b) for a, b in zip(val_list, val_list1)]
        ambiguation = [bother(c, f, n, t) for c, f, n, t in val_list0]
        # print("refine_point_info", conserve)
        # print("refine_point_infoc", conservation)
        # print("refine_val_infof", ambiguation)
        # # print("refine_point_infon", alterationn)
        zipped = list(zip(conservation, perseveration, oposition, deviation, ambiguation))
        df__ = DataFrame(zipped, columns='conservation perseveration oposition deviation ambiguation'.split())
        _df = self.df.drop(columns='game goal trial carta casa move time ponto valor'.split(),
                           inplace=False).reset_index()
        _df = _df.join(df__).drop(columns='level_0 index _id'.split(), inplace=False)
        # self.df = _df
        return _df

    def plot_template(self, cfg: Cfplot, runner, x_lim=None, y_lim=None, df=None):
        """ Template method to embrace a given method.

        :param cfg: Plotting configuration
        :param runner: Given method to be templated.
        :param df: Dataframe source for plotting.
        :param x_lim: Limits for x-axis.
        :param y_lim: Limits for y-axis.
        :return: Plotting context.
        """
        from matplotlib import pyplot as plt_
        f = plt_.figure(figsize=(15, 8))
        ax = f.add_subplot(1, 1, 1)

        if df is None:
            df_ = self.refine_point_value_info()
            df_ = pd.melt(df_, id_vars="name", var_name="measure", value_name="incidence")
        else:
            df_ = df
        chart_ = runner(df_, ax)
        _ = chart_.set(title=cfg.title, ylabel=cfg.ylabel, xlabel=cfg.xlabel)
        # _ = chart_.set_xticklabels(chart_.get_xticklabels(), rotation=45, horizontalalignment='right')
        chart_.set(xlim=x_lim) if x_lim else None
        chart_.set(ylim=y_lim) if y_lim else None
        # chart_.set_xlim(left=x_lim[0], right=x_lim[1]) if x_lim else None
        return plt_

    def plot(self, cfg: Cfplot):
        """ Counting bar plot

        :param cfg: Plotting configuration
        :return: Plotting context.
        """
        import seaborn as sbn
        return self.plot_template(cfg, lambda df_, a: sbn.countplot(data=df_, x="name", hue=cfg.col), df=self.df)

    def factorplot(self, cfg: Cfplot):
        """ Factor bar plot

        :param cfg: Plotting configuration
        :return: Plotting context.
        """
        import seaborn as sbn
        return self.plot_template(cfg, lambda df_, a: sbn.catplot(
            x='name', y='incidence', hue='measure', data=df_, kind='bar'))

    def violinplot(self, cfg: Cfplot):
        """ Violin gaussian plot

        :param cfg: Plotting configuration
        :return: Plotting context.
        """
        import seaborn as sbn
        return self.plot_template(cfg, lambda df_, a: sbn.violinplot(
            x='name', y='incidence', hue='measure', inner="quart", data=df_), y_lim=(None, 10))

    def histplot(self, cfg: Cfplot):
        """ Histogram bar plot

        :param cfg: Plotting configuration
        :return: Plotting context.
        """
        import seaborn as sbn
        return self.plot_template(cfg, lambda df_, a: sbn.histplot(
            data=df_, stat="count", multiple="stack",
            x="incidence", kde=False,
            palette="pastel", hue="measure",
            element="bars", legend=True, ax=a),
                                  x_lim=(9, None), y_lim=(0, 50))

    def heatmap(self, cfg: Cfplot):
        """ Correlation map for cognition profiles

        :param cfg: Plotting configuration
        :return: Plotting context.
        """
        from matplotlib import pyplot as plt_
        plt_.figure(figsize=(15, 8))
        df_ = self.refine_point_value_info()
        df_ = df_.drop(columns=['name'], inplace=False)
        # Compute the correlation matrix
        corr = df_.corr()
        # Generate a mask for the upper triangle
        mask = np.triu(np.ones_like(corr, dtype=bool))
        # Generate a custom diverging colormap
        cmap = sns.diverging_palette(230, 20, as_cmap=True)
        # Draw the heatmap with the mask and correct aspect ratio
        chart_ = sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
                             square=True, linewidths=.5, cbar_kws={"shrink": .5})
        _ = chart_.set(title=cfg.title, ylabel=cfg.ylabel, xlabel=cfg.xlabel)
        return plt_

    def run_plotting(self, kind, data_frame):
        """ Plotting service selector

        :param kind: Selection key
        :param data_frame: Data to be plotted.
        :return: Plotting context
        """
        plotters = dict(value=self.plot, plot=self.plot, factor=self.factorplot,
                        violin=self.violinplot, hist=self.histplot, heat=self.heatmap)
        from dash import Plotting as Plot
        configurations = dict(Plot.plotting)
        configurations[kind].pop("sub_title") if "sub_title" in configurations[kind] else None
        self.retrieve_oid_from_person_df(data_frame)
        return plotters[kind](WiscPlot.Cfplot(**configurations[kind]))


class DashService:
    """ Serviços de plotagem dos dados de Alite-Games.

    """
    name = Cfg.dash_srv

    def __init__(self):
        self.person_url = Cfg.person_url
        self.df: DataFrame = DataFrame()
        self.wisc_plot = WiscPlot()

    @staticmethod
    def person_load(person=Cfg.person_url):
        """ Carrega as informações de dados a partir de um servidor num arcabouço.

        :param person: Url que endereça os dados necessários
        :return: None
        """
        import urllib.request
        import json
        with urllib.request.urlopen(person) as url:
            return json.loads(url.read().decode())

    def general_stats(self):
        from datetime import datetime
        then = datetime(2023, 6, 29)

        def dt(g):
            k, m = g["scorer"][0]["time"], g["scorer"][-1]["time"]
            k, m = pd.to_datetime(k).tz_localize(None), pd.to_datetime(m).tz_localize(None)
            return pd.Timedelta(m - k, unit="min").seconds // 60

        def gm(oid):
            furl = f'https://games.alite.selfip.org/score/games?oid={oid}'
            with urllib.request.urlopen(furl) as url:
                data = json.loads(url.read().decode())
                game = max((dt(g) for g in data if g["scorer"] and g["game"] == "game"), default=0)
                wsct = max((dt(g) for g in data if g["scorer"] and g["game"] == "wsct"), default=0)
                return f"{game} {wsct}"

        df = pd.DataFrame(self.person_load(person='https://games.alite.selfip.org/score/players'))
        df['games_l'] = [[g["game"] for g in t] for t in df.games]
        df['eica'] = [sum([1 for g in t if "game" in g]) for t in df.games_l.tolist()]
        df['wcst'] = [sum([1 for g in t if "wcst" in g]) for t in df.games_l.tolist()]
        df["esc"] = df["ano"].apply(lambda x: int(str(x)[3:]))
        df["ida"] = df["idade"].apply(lambda x: int(str(x)[4:]) + 5)
        df["old"] = df["time"].apply(lambda x: pd.to_datetime(x).tz_localize(None))
        df_rec = df.drop(df[(df.old < then) | (df["esc"] < 6) | (df["esc"] > 9)].index, inplace=False)
        df_rec = df_rec.groupby(['name', 'esc', "ida", "eica", "wcst", "_id"], as_index=False).agg(
            {"_id": "first"}).reset_index()  # .reset_index()
        import re
        # noinspection PyProtectedMember
        matches = [re.findall(r"'(.+?)'", text)[0] for text in df_rec._id.to_list()]
        df_rec["oid"] = matches
        dfo = df_rec.drop('_id', axis=1)
        dfo["ws_ga"] = dfo["oid"].apply(lambda x: gm(x))
        dfo[['gt', 'wt']] = dfo['ws_ga'].str.split(' ', expand=True)
        dfo['wtmx'] = dfo['wt'].apply(lambda x: int(x))
        dfo['gtmx'] = dfo['gt'].apply(lambda x: int(x))
        return dfo

    def games_load(self, games, game='wcst'):
        """ Retrieve games from source

        :param games: original dataframe describing the games
        :param game: which game kind to retrieve
        :return: dataframe with a 'score' column
        """
        dfl = []

        def retrieve_games(player):
            """ Add this player games to the list

            :param player: given player to retrieve games
            :return: expanded list with the games of the given player
            """
            dfl.extend(self.person_load(Cfg.game_url.format(player)))

        def process_df():
            dfg_ = DataFrame(dfl)
            dfx_ = dfg_.explode('scorer')
            dfl_ = DataFrame(dfx_.scorer.values.tolist())
            dfx_ = dfx_.drop(columns=["scorer"], inplace=False).reset_index()
            return dfx_.join(dfl_)

        # retrieve_games('6477cf19f626d3cb95e08c92')
        import re
        _ = game
        # noinspection PyProtectedMember
        matches = [re.findall(r"'(.+?)'", text)[0] for text in games._id.to_list()]
        games["oid"] = matches
        _ = [retrieve_games(oid) for oid in games.oid.to_list()]
        # print(dfl)
        _ = process_df()
        # dfw = dfa.loc[dfa['game'] == game]
        df0 = DataFrame(games.games.to_list())
        df0['score'] = [re.findall(r"'(.+?)'", text)[0] for text in df0.scorer.to_list()]
        return df0

    @rpc
    def plot_wisc(self, games=None, game=None, hue="ponto"):
        dfw = self.games_load(games=games, game=game)
        _ = plt.figure(figsize=(15, 8))
        chart = sns.countplot(data=dfw, x="name", hue=hue)
        _ = chart.set(title='Contagem dos Pontos Wisc', ylabel='Contagem de Pontos', xlabel="Participantes")
        _ = chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment='right')

    @rpc
    def plot_chart(self, chart_index):
        """ Plota um gráfico escolhido no Alite-games.

        :param chart_index: Índice para a coleção de plotagens disponíveis
        :return: O gráfico plotado em forma se sequência codificada em base64
        """
        self.df = DataFrame(self.person_load())
        figure = self.wisc_plot.run_plotting(chart_index, self.df)
        return self.to_base64(figure)

    @rpc
    def plot_pontos(self):
        """ Plota o número de jogos executados no Alite-games.

        :return: O gráfico plotado em forma se sequência codificada em base64
        """
        # import seaborn as sns
        # from matplotlib import pyplot as plt
        dfx = self.general_stats()
        _ = plt.figure(figsize=(15, 8))
        chart = sns.barplot(data=dfx, x="name", y="gtmx", hue="ida")
        _ = chart.set(title='Contagem dos Tempos de Jogo', ylabel='Tempo de Duração de Jogo', xlabel="Participantes")
        _ = chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment='right')
        return self.to_base64()

    def _plot_pontos(self):
        """ Plota o número de jogos executados no Alite-games.

        :return: O gráfico plotado em forma se sequência codificada em base64
        """
        self.df = DataFrame(self.person_load())
        self.df['games_l'] = [[g["game"] for g in t] for t in self.df.games]
        dfx = self.df.explode('games_l')
        _ = plt.figure(figsize=(15, 8))
        chart = sns.countplot(data=dfx, x="name", hue="games_l")
        _ = chart.set(title='Contagem dos Jogos', ylabel='Número de Jogos', xlabel="Participantes")
        _ = chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment='right')
        return self.to_base64()

    @staticmethod
    def to_base64(plt_=plt):
        from io import BytesIO
        img = BytesIO()
        plt_.savefig(img, format='png')
        plt_.close()
        img.seek(0)
        import base64
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        return plot_url
