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
"""Facade for game persistence with MongoDB.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------

.. versionadded::    23.04
        adjust code to game persist (19).
        retrieve load_all as a list (20).
        expand item aggregate working (26)

"""
import pymongo
from pymongo import UpdateOne


def init(passwd, data_base="alite_game", collection="score", db_url="alitelabase.b1lm6fr.mongodb.net"):
    username = "carlotolla9"
    print("ALITE", passwd)
    con_string = f"mongodb+srv://{username}:{passwd}@{db_url}/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(con_string)
    mydb = client[data_base]

    my_col = mydb[collection]
    print("did", my_col)
    return my_col


class Facade:
    def __init__(self, data_base="alite_game", collection="score", db=None):
        self.db = db or init(get_pass(), data_base=data_base, collection=collection)

    def load_all(self):
        dbt = self.db.find({"games": {"$exists": True}})
        return [ob for ob in dbt]

    def load_player(self, oid):
        # kind = dict(task="task", step="step", LABA="board")
        query = [{'$lookup':
                      {'from': 'models',
                       'localField': 'oid',
                       'foreignField': 'ply_id',
                       'as': 'score'}},
                 {'$unwind': '$score'},
                 {'$match': {'oid': oid}},
                 {'$project':
                      {'authors': 1, 'cellmodels.celltypes': 1}}
                 ]
        # dbt = self.db.find_one(filter={"oid": oid}) if item_dict else self.db.find_one()
        dbt = self.db.find_one(filter={"oid": oid}) or self.db.find_one()
        print("dbt", dbt)
        return dbt

    def load_item(self, item_dict):
        # kind = dict(task="task", step="step", LABA="board")
        dbt = self.db.find_one(filter=item_dict) if item_dict else self.db.find_one()
        print("dbt", dbt)
        return dbt

    def upsert(self, items, idx="oid", _idx="_id"):
        _ = items.pop(_idx) if _idx in items else None
        ids = items.pop(idx)
        self.db.update_one({idx: ids}, {'$set': items}, upsert=True)

    def save_all(self, items, idx="oid", _idx="_id"):
        _ = [data.pop(_idx) for data in items if _idx in items]
        _ids = [data.pop(idx) for data in items]
        operations = [UpdateOne({idx: idn}, {'$set': data}, upsert=True) for idn, data in zip(_ids, items)]
        self.db.bulk_write(operations)

    def expand_item(self, oid):
        aggregate = [
            {
                '$match': {
                    'doc_id': oid
                }
            },
            {
                '$lookup': {
                    'from': 'score',
                    'localField': 'games',
                    'foreignField': 'doc_id',
                    'as': 'games'
                }
            },
            {
                '$unwind': '$games'
            },
            {
                '$group': {
                    '_id': '$_id',
                    'products': {
                        '$push': '$games'
                    }
                }
            }
        ]
        aggregate1 = [
            {
                '$match': {
                    'doc_id': oid
                }
            },
            {
                '$unwind': "$games"
            },
            {
                '$lookup': {
                    'from': 'score',
                    'localField': 'games',
                    'foreignField': 'doc_id',
                    'as': 'games'
                }
            },
            {
                '$unwind': "$games.0.score"
            },
            {
                '$lookup': {
                    'from': 'score',
                    'localField': 'games.0.score',
                    'foreignField': 'doc_id',
                    'as': 'scorer'
                }
            },
            {
                '$group': {
                    '_id': {
                        '_id': '$_id',
                        'doc_id': '$doc_id',
                        'game': '$games.0.game',
                        'goal': '$games.0.goal',
                    },
                    'score': {'$push': '$scorer.0'}
                }
            }
        ]
        result = self.db.aggregate(aggregate1)

        def scorer(sco):
            return [{k: v for k, v in sc.items() if k in "marker"} for sc in sco]
        result = [{k if k != "_id" else "game_goal": (v['game'], v['goal']) if k == "_id" else scorer(v)
                   for k, v in gm.items()} for gm in result]
        return result


def get_pass():
    with open("../../../..env", "r") as env:
        return env.read().split("=")[1].strip('"')


def local_up():
    passwd = get_pass()
    print(passwd)
    username = "carlotolla9"
    # db_url = "mongo"
    # con_string = f"mongodb://{username}:{passwd}@{db_url}/?retryWrites=true&w=majority"
    dbs = pymongo.MongoClient(host="0.0.0.0", username=username, password=passwd).list_database_names()
    print("dbs", dbs)


def game_populate():
    global DS
    DS = Facade(data_base="alite_game", collection="score")
    data = {'doc_id': '824909783', 'carta': '__A_T_I_V_A__', 'casa': '0_0',
            'move': 'ok', 'ponto': '_MUNDO_', 'valor': True}
    DS.upsert(data, idx="doc_id")


DS = None  # Facade()

if __name__ == '__main__':
    # Persist().load_item(None)
    # its = populate()
    # DS.save_all(its)
    # _dct = DS.load_all()
    # [pprint({_lt: _it}) for _lt, _it in _dct.items()]
    # print(DS.db.create_index([('pid', pymongo.ASCENDING)]))
    # [pprint(it) for it in DS.db.find()]
    # Persist().load_item(dict(oid="task11"))
    # Persist().save_all(populate())
    # atlas_up()
    # local_up()
    game_populate()
