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
"""Model persistence with MongoDB.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------

.. versionadded::    23.03
        spike connect to atlas (07).
        try connection with local mongo (08).
        return JSON format for KanbanModel argument (08).
        up many now working (09).
        fix task_ids and _id in populated atlas (14).
        fix Persist upsert argument _idx="_id" (22).

"""
from pprint import pprint

import pymongo
from pymongo import UpdateOne


def init(passwd):
    # passwd = os.environ['ALITE']
    username = "carlotolla9"
    print("ALITE", passwd)
    db_url = "alitelabase.b1lm6fr.mongodb.net"
    con_string = f"mongodb+srv://{username}:{passwd}@{db_url}/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(con_string)
    mydb = client.alite_kanban

    mycol = mydb["tasks"]
    print("did", mycol)
    return mycol


def populate():
    with open("kbj.json", "r") as fjson:
        # mycol = init(get_pass())
        import json
        '''items = json.load(fjson)["KanbanModel"]["tasks"]
        for task, fields in items.items():
            print(task, fields["Task"])'''
        items = json.load(fjson)
        # items = json.load(fjson)["KanbanModel"]["tasks"]
        docs = [fields for task, fields in items.items()]
        [print(item) for item in docs]
        return docs
        # res = mycol.insert_many(docs)
        # print(res.inserted_ids)


class Persist:
    def __init__(self):
        # _client = pymongo.MongoClient(con_string)
        self.db = init(get_pass())
        # self.db = _client.alite_kanban

    def load_all(self):
        # kind = dict(task="task", step="step", LABA="board")
        def task(oid="", parent_id=None, desc=None, color_id=0, progress=0, _id=0, pid=0,
                 task_ids=(), tags=(), users=(), calendar=(), comments=(), external_links=()):
            return dict(oid=str(oid), parent_id=str(parent_id), desc=str(desc), color_id=str(color_id),
                        progress=progress, _id=str(_id), task_ids=task_ids, tags=tags, users=users,
                        calendar=calendar, comments=comments, external_links=external_links)
        def board(oid=None, parent_id="", counter=1, schema_revision="", _id=0, pid=0,
                  steps_colors=(), tasks_colors=(), task_ids=(), current="", desc=""):
            return dict(oid=str(oid), parent_id=str(parent_id), desc=str(desc),
                        _id=str(_id), task_ids=task_ids, steps_colors=steps_colors, schema_revision=schema_revision,
                        tasks_colors=tasks_colors, counter=counter, current=current)
        loader = dict(step=task, task=task, boar=board)

        dbt = self.db.find()
        # return dbt
        lst = [{k: v for k, v in task.items()} for task in dbt]
        _dict = {args["oid"] if args["oid"][0] in "st" else "board": loader[args["oid"][:4]](**args)
                 for args in lst if "oid" in args}
        return _dict

    def load_item(self, item_dict):
        # kind = dict(task="task", step="step", LABA="board")
        dbt = self.db.find_one(filter=item_dict) if item_dict else self.db.find_one()
        print("dbt", dbt)
        return dbt

    def upsert(self, items, idx="oid", _idx="_id"):
        _ = items.pop(_idx) if _idx in items else None
        ids = items.pop(idx)
        self.db.update_one({idx: ids}, {'$set': items},  upsert=True)

    def save_all(self, items, idx="oid", _idx="_id"):
        _ = [data.pop(_idx) for data in items if _idx in items]
        ids = [data.pop(idx) for data in items]
        # ids = [data.pop("_id") for data in items]
        operations = [UpdateOne({idx: idn}, {'$set': data}, upsert=True) for idn, data in zip(ids, items)]
        # operations = [UpdateOne({"_id": idn}, {'$set': data}, upsert=True) for idn, data in zip(ids, items)]
        self.db.bulk_write(operations)


def atlas_up():
    pst = Persist()
    dct = pst.load_all()

    [print({dc: dcv}) for dc, dcv in dct.items()]


def _atlas_up():
    # populate()
    mycol = init(get_pass())
    # result = mycol.create_index([('oid', pymongo.ASCENDING)])
    # print("index", result)
    dat = {_oid["oid"]: {key: str(value) for key, value in _oid.items()} for _oid in mycol.find()}
    for key, value in dat.items():  # ({"oid": "step1"}, {"_id": 0}):
        data = {key: value}
        # data = {key: str(value) for key, value in x.items()}
        print(data)


def get_pass():
    with open("../../.env", "r") as env:
        return env.read().split("=")[1].strip('"')


def local_up():
    passwd = get_pass()
    print(passwd)
    username = "carlotolla9"
    # db_url = "mongo"
    # con_string = f"mongodb://{username}:{passwd}@{db_url}/?retryWrites=true&w=majority"
    dbs = pymongo.MongoClient(host="0.0.0.0", username=username, password=passwd).list_database_names()
    print("dbs", dbs)


def _local_up():
    with open("../../.env", "r") as env:
        passwd = env.read().split("=")[1].strip('"')
        print(passwd)
        username = "carlotolla9"
        db_url = "mongo"
        con_string = f"mongodb://{username}:{passwd}@{db_url}/?retryWrites=true&w=majority"
        dbs = pymongo.MongoClient(con_string).list_database_names()
        print("dbs", dbs)


DS = Persist()


if __name__ == '__main__':
    # Persist().load_item(None)
    # its = populate()
    # DS.save_all(its)
    _dct = DS.load_all()
    [pprint({_lt: _it}) for _lt, _it in _dct.items()]
    # print(DS.db.create_index([('pid', pymongo.ASCENDING)]))
    # [pprint(it) for it in DS.db.find()]
    # Persist().load_item(dict(oid="task11"))
    # Persist().save_all(populate())
    # atlas_up()
    # local_up()
