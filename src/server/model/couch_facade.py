#! /usr/bin/env python
# -*- coding: UTF8 -*-
""" Interface com o banco couchdb

Changelog
---------
.. versionadded::    23.08
   |br| conversão da mongo :class:`Facade` (12)
   |br| adiciona o método de atualização :meth:`Facade.update` (14)

Funções do Documento de projeto no CouchDB
---------------------------------------------

   _design/all/_update:
   function(doc, req) {if (!doc) {return [null,
   {'code': 400,'json': {'error': 'missed','reason': 'no document to update'}}]}
    else {doc.pod.push(req.body);return [doc, {'json':{'status': 'ok'}}];}}

    function(doc, req) {if (!doc) {return [null,
    {'code': 400,'json': {'error': 'missed','reason': 'no document to update'}}]}
     else {doc['name'] = req['form']['name'];return [doc, {'json':{'status': 'ok'}}];}}

|   **Open Source Notification:** This file is part of open source program **Alite**
|   **Copyright © 2023  Carlo Oliveira** <carlo@nce.ufrj.br>,
|   **SPDX-License-Identifier:** `GNU General Public License v3.0 or later <http://is.gd/3Udt>`_.
|   `Labase <http://labase.selfip.org/>`_ - `NCE <http://portal.nce.ufrj.br>`_ - `UFRJ <https://ufrj.br/>`_.

"""
__version__ = "23.08"
import pycouchdb
from dash import MongoConfiguration as Cfg


def update(self, name, oid, data=None, wrapper=None, flat=None, as_list=False, **kwargs):
    """
    Execute a design document view query.

    :param data: data to be sent in update request
    :param name: name of the view (eg: docidname/viewname).
    :param wrapper: wrap result into a specific class.
    :param as_list: return a list of results instead of a
        default lazy generator.
    :param flat: get a specific field from a object instead
        of a complete object.

    .. versionadded: 1.4
       Add as_list parameter.
       Add flat parameter.

    :returns: generator object
    """
    import copy
    params = copy.copy(kwargs)
    from pycouchdb import utils
    path = utils._path_from_name(name, '_update') + [oid]
    data = data

    if "keys" in params and not data:
        import json
        data = utils.force_bytes(json.dumps(params.pop('keys')))

    params = utils.encode_view_options(params)
    resource = self.resource(*path)

    if data is None:
        (resp, result) = resource.get(params=params, headers=None)
    else:
        (resp, result) = resource.post(
            data=data, params=params, headers=None)

    # result = self._query(self.resource(*path), wrapper=wrapper,
    #                      flat=flat, params=params, data=data)

    if as_list:
        return list(result)
    return result


pycouchdb.client.Database.update = update


class Facade:
    def __init__(self, collection="score", dot="today", db=None):
        con = Cfg.cdb_url
        self.dot = dot
        self.db = db if db else pycouchdb.Server(con).database(collection)

    def load_all(self):
        dbt = self.db.all(as_list=True)
        # return [ob for ob in dbt]
        return list(dbt)

    def load_players(self, dot=None):
        dot = dot or self.dot
        dbt = list(self.db.query("all/by_dot_oid", key=dot))
        # print("load_player dbt", oid, dbt)
        return dbt or dict(_id=f"THIS ID: {dot} WAS NOT FOUND")

    def load_item(self, oid):
        dbt = self.db.get(oid) or dict(_id=f"THIS ID: {oid} WAS NOT FOUND")
        return dbt

    def insert(self, items):
        print(items)
        ids = self.db.save(items)
        return ids  # .inserted_id

    def upsert(self, items, _idx="_id", op="$set"):
        oid = items[_idx] if _idx in items else None
        _items = self.db.get(oid) if oid else items
        _items.update(items)
        # ids = items.pop(idx) if idx in items else str(uuid.uuid4().fields[-1])[:9]
        return self.insert(_items)

    def update(self, updater, oid, data=None, **kwargs):
        return self.db.update(updater,  oid, data, **kwargs)

    def query(self, view, **kwargs):
        return self.db.query(view, **kwargs)

    def expand_item(self, oid):
        pass

    def add_game(self, person, game, goal=0, trial=0):
        oid, scorer, trials = self.__find_trial(person, game, goal=goal, trial=trial)
        self.db.update_one({'_id': oid},
                           {'$push': {'games': dict(game=game, goal=goal, trial=trials, scorer=scorer)}}, upsert=True)
        # print("add_game, scorer, trial", scorer, trial)
        return scorer, trials

    def __find_trial(self, person, game, goal=0, trial=0):
        _ = goal, trial
        oid = person
        scorer = self.insert(dict(score=()))
        item_dict = dict(_id=oid)
        trials = self.db.find_one(filter=item_dict)
        trials = trials["games"] if "games" in trials else []
        trials = [trial_ for trial_ in trials if trial_["game"] == game]
        return oid, scorer, len(trials)

    def score(self, items, score_id=None):
        self.db.update_one({'_id': score_id}, {'$push': {'score': items}}, upsert=True)
        return score_id


DS = None  # Facade()

if __name__ == '__main__':
    REV, OID, NAME = "_rev _id name".split()
    fc = Facade()
    sl = fc.load_all()
    s0 = sl[0]
    assert 4 <= len(sl), sl
    assert "id" in s0, s0
    si = s0["id"]
    sd = dict(fc.load_item(si))
    assert 'name' in sd, sd
    assert REV in sd, (REV, sd)
    sr = sd[REV]
    sn = {OID: si, REV: sr, NAME: 'FOO_X'}
    sg = fc.update("all/up_game", "3fe8e4eebc3f48f5804df041690d2b40", keys=dict(n="o"))
    # sg = fc.update("all/up_game", "3fe8e4eebc3f48f5804df041690d2b40", data="m")
    assert "g" in sg, sg

    # su = fc.upsert(sn)
    # assert su == sn, (su, sn)
    # ids = items.pop(idx) if idx in items else str(uuid.uuid4().fields[-1])[:9]

