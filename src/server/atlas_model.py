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

"""
import pymongo
import os
passwd = os.environ['ALITE']
username = "carlotolla9"
print("ALITE", passwd)
db_url = "alitelabase.b1lm6fr.mongodb.net"
con_string = f"mongodb+srv://{username}:{passwd}@{db_url}/?retryWrites=true&w=majority"
client = pymongo.MongoClient(con_string)
mydb = client.alite_kanban

mycol = mydb["tasks"]
print("did", mycol)


def populate():
    with open("kbj.json", "r") as fjson:
        import json
        '''items = json.load(fjson)["KanbanModel"]["tasks"]
        for task, fields in items.items():
            print(task, fields["Task"])'''
        items = json.load(fjson)["KanbanModel"]["tasks"]
        docs = [fields["Task"] for task, fields in items.items()]
        [print(item) for item in docs]
        res = mycol.insert_many(docs)
        print(res.inserted_ids)


class Persist:
    def __init__(self):
        _client = pymongo.MongoClient(con_string)
        self.db = _client.alite_kanban

    def load_all(self):
        return [task for task in self.db.find()]

    def save_all(self, items):
        from pymongo import UpdateOne
        ids = [data.pop("_id") for data in items]
        operations = [UpdateOne({"_id": idn}, {'$set': data}, upsert=True) for idn, data in zip(ids, items)]
        self.db.bulk_write(operations)


if __name__ == '__main__':

    # populate()
    result = mycol.create_index([('oid', pymongo.ASCENDING)])
    print("index", result)
    for x in mycol.find():  # ({"oid": "step1"}, {"_id": 0}):
        print(x)
