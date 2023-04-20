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

.. versionadded::    23.04
        initial version (19).
        improved web and mongo testing (20).

"""
import unittest
import mongomock
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import Application
from tornado.httpserver import HTTPRequest
from unittest.mock import Mock
import game_main as game
from model.game_facade import Facade
MONGO = [
    dict(doc_id=0, games=[1]),
    dict(doc_id=1, ply_id=0, game=2, score=[[4, 5]]),
    dict(doc_id=2, ply_id=3, game=1, score=[[6, 7, 8]]),
    dict(doc_id=3, games=[2]),
    dict(doc_id=4, ply_id=0, marker=1),
    dict(doc_id=5, ply_id=0, marker=2),
    dict(doc_id=6, ply_id=3, marker=1),
    dict(doc_id=7, ply_id=3, marker=2),
    dict(doc_id=8, ply_id=3, marker=2),
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
        collection = mongomock.MongoClient().db.collection
        objects = MONGO
        # objects = [dict(doc_id=0, games=1), dict(doc_id=0, game=2), dict(doc_id=0, game=1), dict(doc_id=0, games=2)]
        collection.insert_many(objects)
        self.facade = Facade(db=collection)

    def test_list_mongo(self):
        # collection = mongomock.MongoClient()
        dbs = mongomock.MongoClient(host="0.0.0.0", username="username", password="passwd").list_database_names()
        print("dbs", dbs)
        self.assertEqual(dbs, [])  # add assertion here

    def test_find_players(self):
        self._init_mongo()

        found = self.facade.load_all()
        # found = collection.find({"games": {"$exists": True}})
        self.assertEqual(2, len(found))

    def test_find_one_player(self):
        self._init_mongo()

        found = self.facade.load_item(dict(doc_id=0))
        # found = collection.find({"games": {"$exists": True}})
        self.assertEqual(0, found['doc_id'], f"found: {found}")


if __name__ == '__main__':
    unittest.main()
