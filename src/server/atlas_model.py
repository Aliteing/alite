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
        return JSON format for KanbamModel argument (08). up many fail.

"""
import pymongo


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
        kind = dict(task="task", step="step", LABA="board")
        lst = [{k: str(v) for k, v in task.items()} for task in self.db.find()]
        _dct = {args["oid"] if args["oid"][0] in "st" else "board": args for args in lst if "oid" in args}
        return _dct

    def save_all(self, items):
        from pymongo import UpdateOne
        ids = [data.pop("_id") for data in items]
        operations = [UpdateOne({"_id": idn}, {'$set': data}, upsert=True) for idn, data in zip(ids, items)]
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


if __name__ == '__main__':
    Persist().save_all(populate())
    # atlas_up()
    # local_up()
