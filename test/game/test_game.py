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
"""Game testing for web API and database facade.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------

.. versionadded::    23.05
        redefine doc_id into _id (03).
        added test for goal, trials, trial (09).

.. versionadded::    23.04
        initial version (19).
        improved web and mongo testing (20).
        test expand item mongo passing (26).
        add score and add game passing (27).

"""
import unittest
import mongomock
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import Application
from tornado.httpserver import HTTPRequest
from unittest.mock import Mock
import game_main as game
from model.game_facade import Facade
MONG_ = [
    dict(doc_id=0, games=[1, 2]),
    dict(doc_id=1, ply_id=0, game=2, goal=0, score=[4, 5]),
    dict(doc_id=2, ply_id=3, game=1, goal=0, score=[6, 7, 8]),
    # dict(doc_id=1, ply_id=0, game=2, score=[[4, 5]]),
    # dict(doc_id=2, ply_id=3, game=1, score=[[6, 7, 8]]),
    dict(doc_id=3, games=[2]),
    dict(doc_id=4, ply_id=0, marker=1),
    dict(doc_id=5, ply_id=0, marker=2),
    dict(doc_id=6, ply_id=3, marker=11),
    dict(doc_id=7, ply_id=3, marker=12),
    dict(doc_id=8, ply_id=3, marker=13),
]

MONGO = [
    dict(name=0, games=[dict(game=2, goal=0, trial=0, scorer=()), dict(game=2, goal=0, trial=1, scorer=())]),
    dict(name=1, games=[dict(game=2, goal=0, trial=0, scorer=()), dict(game=2, goal=0, trial=1, scorer=())]),
    dict(name=2, games=[dict(game=2, goal=0, trial=0, scorer=()), dict(game=2, goal=0, trial=1, scorer=())]),
    dict(score=(dict(marker=1), dict(marker=2))),
    dict(score=(dict(marker=21), dict(marker=22))),
    dict(score=(dict(marker=11), dict(marker=12), dict(marker=13))),
    dict(score=(dict(marker=111), dict(marker=112), dict(marker=113))),
]
MONGA = [
    dict(name=0, games=[dict(game=2, goals=[dict(trials=(dict(trial=()),))])]),
    dict(name=1, games=[dict(game=2, goals=[dict(trials=(dict(trial=()),))])]),
    dict(name=2, games=[dict(game=1, goals=[dict(trials=(dict(trial=()),))])]),
    dict(score=(dict(marker=1), dict(marker=2),)),
    dict(score=(dict(marker=21), dict(marker=22),)),
    dict(score=(dict(marker=11), dict(marker=12), dict(marker=13),)),
    dict(score=(dict(marker=111), dict(marker=112), dict(marker=113),)),
]

SCORE = [
    dict(score=(dict(marker=301), dict(marker=302),)),
    dict(score=(dict(marker=321), dict(marker=322),)),
    dict(score=(dict(marker=11), dict(marker=412), dict(marker=413),)),
    dict(score=(dict(marker=111), dict(marker=512), dict(marker=513),)),
]


class TestSomeHandler(AsyncHTTPTestCase):
    def get_app(self):
        return game.make_app()

    def test_homepage(self):
        response = self.fetch("/")
        self.assertEqual(200, response.code, "failed retrieve main")
        self.assertIn(b"Jogo Eica - Cadastro", response.body)

    def test_get_game_id(self):
        response = self.fetch(r"/record/oid")
        self.assertEqual(200, response.code, "failed retrieve gameid")
        self.assertEqual(9, len(response.body), "unexpected id size")

    def test_post_score(self):
        response = self.fetch(r"/record/store", False, method="POST", body='{"oid": "123"}')
        self.assertEqual(200, response.code, "failed post_score")
        self.assertEqual(0, len(response.body), "unexpected id size")

    @gen_test
    def __test_no_from_date_param(self):
        mock_application = Mock(spec=Application)
        payload_request = HTTPRequest(
            method='GET', uri='/', headers=None, body=None
        )
        handler = game.MainPage(mock_application, payload_request)
        with self.assertRaises(ValueError):
            yield handler.get()


class TestGameFacade(unittest.TestCase):
    def _init_mongo(self):
        # collection = mongomock.MongoClient()
        collection = mongomock.MongoClient().db.create_collection('score')
        # collection = mongomock.MongoClient().db.collection
        objects = MONGO
        # objects = [dict(doc_id=0, games=1), dict(doc_id=0, game=2), dict(doc_id=0, game=1), dict(doc_id=0, games=2)]
        collection.insert_many(objects)
        self.person = person = [it['_id'] for it in collection.find({'name': {'$exists': True}})]
        score = [it for it in collection.find({'score': {'$exists': True}})]
        self.score = [it['_id'] for it in score]
        populate = [(per, score[i: i+1]) for i, per in enumerate(person)]
        print('len(person), len(score), len(populate)', len(person), len(score), len(populate))
        [print(sc[0]) for sc in populate]

        # [collection.update_one({'_id': ids}, {'$push': {'games.0.goals.0.trials.0.trial': item['_id']}}, upsert=True)
        [collection.update_one({'_id': ids}, {'$push': {f'games.{gamer}.score': item['_id']}}, upsert=True)
         for ids, items in populate for gamer, item in enumerate(items)]

        self.facade = Facade(db=collection)
        print(self.facade.load_item(dict(_id=person[0])))

    def test_list_mongo(self):
        # collection = mongomock.MongoClient()
        dbs = mongomock.MongoClient(host="0.0.0.0", username="username", password="passwd").list_database_names()
        print("dbs", dbs)
        self.assertEqual(dbs, [])  # add assertion here

    def test_find_players(self):
        self._init_mongo()

        found = self.facade.load_all()
        # found = collection.find({"games": {"$exists": True}})
        self.assertEqual(3, len(found))

    def test_find_one_player(self):
        self._init_mongo()
        player = self.person[0]

        found = self.facade.load_item(dict(_id=player))
        self.assertEqual(player, found['_id'], f"found: {found}")

    def test_expand_one_player(self):
        self._init_mongo()
        player = self.person[2]

        found = self.facade.expand_item(player)
        fnd = str([fn for fn in found])
        as_str = "'scorer': [{'marker': 11}, {'marker': 12}, {'marker': 13}]"
        self.assertIn(as_str, fnd, f"found: {fnd}")

    def test_add_score(self):
        self._init_mongo()
        scorer = self.score[0]
        self.facade.score(dict(marker=22), scorer)
        gamer = self.facade.load_item(dict(_id=scorer))
        as_str = "'score': [{'marker': 1}, {'marker': 2}, {'marker': 22}"
        self.assertIn(as_str, str(gamer), f"found: {gamer}")
        found = self.facade.expand_item(self.person[0])
        fnd = str([fn for fn in found])
        as_str = "'scorer': [{'marker': 1}, {'marker': 2}, {'marker': 22}]"
        self.assertIn(as_str, fnd, f"found: {fnd}")

    def test_add_game(self):
        self._init_mongo()
        person = self.person[0]
        self.facade.add_game(person=person, game=3)  # dict(game=3, goals=())})
        gamer = self.facade.load_item(dict(_id=person))
        self.assertEqual(person, gamer["_id"], f"found gamer: {gamer}, person: {person}")
        as_str = "{'game': 3, 'goal': 0, 'trial': 0, 'scorer': []}"
        self.assertIn(as_str, str(gamer), f"found in games: {gamer['games']}")
        found = self.facade.expand_item(person)
        fnd = str([fn for fn in found])
        as_str = "{'game': 3, 'goal': 0, 'trial': 0, 'scorer': []}"
        self.assertIn(as_str, fnd, f"found: {fnd}")

    def _add_goal(self):
        self._init_mongo()
        person = self.person[0]
        trials = {'trials': [{'trial': ()}]}
        self.facade.db.update_one({'_id': person}, {'$push': {'games': dict(game=3, goals=())}}, upsert=True)
        self.facade.db.update_one({'_id': person}, {'$push': {'games.0.goals': trials}}, upsert=True)
        self.facade.db.update_one({'_id': person}, {'$push': {'games.1.goals': trials}}, upsert=True)
        return person

    def _test_add_goal(self):
        person = self._add_goal()
        gamer = self.facade.load_item(dict(_id=person))
        as_str = "{'trials': [{'trial': []}]}]}, {'game': 3, 'goals': [{'trials': [{'trial': []}]}]}"
        self.assertIn(as_str, str(gamer), f"found: {gamer['games']}")
        found = self.facade.expand_item(person)
        fnd = str([fn for fn in found])
        as_str = "'name': 0, 'game': 2}}, {'trial': [[]]"
        self.assertIn(as_str, fnd, f"found: {fnd}")

    def _test_add_trial(self):
        person = self._add_goal()
        trial = {'trial': ()}
        self.facade.db.update_one({'_id': person}, {'$push': {'games.0.goals.1.trials': trial}}, upsert=True)
        oid = self.facade.db.insert_one(document=dict(score=[dict(marker=1234)]))
        # self.assertEqual(0, str(oid))
        self.facade.db.update_one(
            {'_id': person}, {'$push': {'games.0.goals.1.trials.1.trial': oid.inserted_id}}, upsert=True)
        gamer = self.facade.load_item(dict(_id=person))
        as_str = ("{'trial': [ObjectId('" + str(oid.inserted_id) +
                  "')]}]}]}, {'game': 3, 'goals': [{'trials': [{'trial': []}]}]}]")
        self.assertIn(as_str, str(gamer), f"found: {gamer['games']}")
        found = self.facade.expand_item(person)
        fnd = str([fn for fn in found])
        as_str = str([dict(marker=1234)])
        self.assertIn(as_str, fnd, f"found: {fnd}")


if __name__ == '__main__':
    unittest.main()
