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

.. versionadded::    23.05
        redefine doc_id into _id (03).
        add score & add_game (09).
        refactor session & expand format (10).
        fix add game and conform to web call (10).
        add trial to add_game & add_trial (24).
        fix get_pass .env path (25)
        new expand, fix add_game for trials (25a).
        add tornado options to db connect string (28)

.. versionadded::    23.04
        adjust code to game persist (19).
        retrieve load_all as a list (20).
        expand item aggregate working (26).
        score items operation working (27).

"""
import pymongo
import uuid
from bson.objectid import ObjectId
from tornado.options import options


def init(data_base="alite_game", collection="score", con_string=None):
    con_string = con_string or options.dbcon
    client = pymongo.MongoClient(con_string)
    mydb = client[data_base]

    my_col = mydb[collection]
    print("Connected to collection:", my_col)
    return my_col


class Facade:
    def __init__(self, data_base="alite_game", collection="score", db=None):
        con = options.dbcon
        self.db = db if db else init(data_base=data_base, collection=collection, con_string=con)

    def load_any(self):
        dbt = self.db.find()
        return [ob for ob in dbt]

    def load_all(self):
        dbt = self.db.find({"games": {"$exists": True}})
        return [ob for ob in dbt]

    def load_player(self, oid):
        dbt = self.db.find_one(filter={"oid": oid}) or self.db.find_one()
        print("dbt", dbt)
        return dbt

    def load_item(self, item_dict):
        if item_dict and "_id" in item_dict:
            item_dict["_id"] = id_ if (id_ := item_dict["_id"]) is ObjectId else ObjectId(id_)
        dbt = self.db.find_one(filter=item_dict) if item_dict else self.db.find_one()
        return dbt

    def insert(self, items):
        ids = self.db.insert_one(items)
        return ids.inserted_id

    def upsert(self, items, idx="doc_id", _idx="_id", op="$set"):
        _ = items.pop(_idx) if _idx in items else None
        ids = items.pop(idx) if idx in items else str(uuid.uuid4().fields[-1])[:9]
        self.db.update_one({idx: ids}, {op: items}, upsert=True)
        return ids

    def expand_item(self, oid):
        aggregate1 = [
            {
                '$match': {
                    '_id': oid
                }
            },
            {
                '$unwind': {
                    'path': '$games',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$lookup': {
                    'from': 'score',
                    'localField': 'games.scorer',
                    'foreignField': '_id',
                    'as': 'scoring'
                }
            },
            {
                '$project': {
                    'name': '$name',
                    "game": "$games.game",
                    "goal": "$games.goal",
                    "trial": "$games.trial",
                    'scorer': {'$ifNull': ['$scoring.score', []]},
                }
            },
        ]
        result = self.db.aggregate(aggregate1)
        return result

    def add_game(self, person, game, goal=0, trial=0):
        oid, scorer, trials = self.__find_trial(person, game, goal=goal, trial=trial)
        self.db.update_one({'_id': oid},
                           {'$push': {'games': dict(game=game, goal=goal, trial=trials, scorer=scorer)}}, upsert=True)
        # print("add_game, scorer, trial", scorer, trial)
        return scorer, trials

    def __find_trial(self, person, game, goal=0, trial=0):
        oid = person if person is ObjectId else ObjectId(person)
        scorer = self.insert(dict(score=()))
        item_dict = dict(_id=oid)
        trials = self.db.find_one(filter=item_dict)
        trials = trials["games"] if "games" in trials else []
        trials = [trial_ for trial_ in trials if trial_["game"] == game]
        return oid, scorer, len(trials)

    def score(self, items, score_id=None):
        score_id = score_id if score_id is ObjectId else ObjectId(score_id)
        self.db.update_one({'_id': score_id}, {'$push': {'score': items}}, upsert=True)
        return score_id


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
    # game_populate()
    pass
