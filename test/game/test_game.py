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
        added test for user, game, score (10).
        web tests for mongomock, fix add_game (10).
        adding seven tests for wisconsin game (18).
        include score testing for wisconsin (19).
        fixed test for adding goal to game (23).
        test add_game & add_trial with url arguments (24)

.. versionadded::    23.04
        initial version (19).
        improved web and mongo testing (20).
        test expand item mongo passing (26).
        add score and add game passing (27).

"""
import json
import unittest
import mongomock
from tornado.testing import AsyncHTTPTestCase
from unittest.mock import MagicMock
import game_main as game
from model.game_facade import Facade
from wcst import Wisconsin, Carta
from urllib.parse import urlencode

MONGO = [
    dict(name=0, games=[dict(game=2, goal=0, trial=0, scorer=()), dict(game=2, goal=0, trial=1, scorer=())]),
    dict(name=1, games=[dict(game=2, goal=0, trial=0, scorer=()), dict(game=2, goal=0, trial=1, scorer=())]),
    dict(name=2, games=[dict(game=2, goal=0, trial=0, scorer=()), dict(game=2, goal=0, trial=1, scorer=())]),
    dict(score=(dict(marker=1), dict(marker=2))),
    dict(score=(dict(marker=21), dict(marker=22))),
    dict(score=(dict(marker=11), dict(marker=12), dict(marker=13))),
    dict(score=(dict(marker=111), dict(marker=112), dict(marker=113))),
]


class TestSomeHandler(AsyncHTTPTestCase):
    def get_app(self):
        collection = mongomock.MongoClient().db.create_collection('score')
        self.db = Facade(db=collection)
        return game.make_app(ds=self.db)

    def test_homepage(self):
        response = self.fetch("/")
        self.assertEqual(200, response.code, "failed retrieve main")
        self.assertIn(b"Jogo Eica - Cadastro", response.body)

    def _post_add_game(self, oid, jogo=88, goal=0, trial=0):
        body = dict(person=str(oid), game=jogo, goal=goal, trial=trial)
        from urllib.parse import urlencode
        data = urlencode(body)
        # print("add_game", body)
        response = self.fetch(r"/record/store", False, method="POST", body=data)
        self.assertEqual(200, response.code, "failed add_game")
        self.assertLessEqual(24, len(response.body), "unexpected id size")
        user = (self.db.load_any())
        oid = response.body.decode("utf8")[0]
        # [print(f"obj: {u}") for u in self.db.load_any()]
        self.assertIn(oid, str(user), f"oid {oid} not in user {user}")
        return user

    def _get_a_page(self, uri, **kwargs):
        body = kwargs
        data = urlencode(body)
        print("add_game", data)
        response = self.fetch(uri + "?" + data, False, method="GET")
        self.assertEqual(200, response.code, "failed get add_game")
        self.assertLess(4000, len(response.body), "unexpected id size")
        # user = (self.db.load_any())
        page = response.body.decode("utf8")
        # [print(f"obj: {u}") for u in self.db.load_any()]
        # self.assertIn(oid, str(page), f"oid {oid} not in user {user}")
        return page

    def test_get_games_page(self):
        oid = str(self.db.insert(dict(name=357, year=5, gander="outro", age=12, games=())))
        page = self._get_a_page(r"/home/games", oid=oid)
        self.assertIn(oid, page, f"oid {oid} not in user {page}")

    def test_get_eica_page(self):
        oid = str(self.db.insert(dict(name=357, year=5, gander="outro", age=12, games=())))
        page = self._get_a_page(r"/home/game", oid=oid, game=88, goal=0, trial=0)
        # self.assertIn(oid, page, f"oid {oid} not in user {page}")
        gamer = "88"
        self.assertIn(gamer, page, f"oid {gamer} not in user {page}")

    def test_get_wisconsin_page(self):
        oid = str(self.db.insert(dict(name=357, year=5, gander="outro", age=12, games=())))
        page = self._get_a_page(r"/home/wcst", oid=oid, game=88, goal=0, trial=0)
        # self.assertIn(oid, page, f"oid {oid} not in user {page}")
        gamer = "88"
        self.assertIn(gamer, page, f"oid {gamer} not in user {page}")

    def test_get_wisconsin_page_new_trial(self):
        oid = str(self.db.insert(dict(name=358, year=6, gander="outro", age=12, games=())))
        page = self._get_a_page(r"/home/wcst", oid=oid, game="wsct", goal=22, trial=0)
        found = self.db.load_item(None)
        self.assertIn(oid, str(found), f"oid {oid} not in user {page}")
        gamer = str(found["games"][0]["scorer"][0])
        page = self._get_a_page(r"/home/wcst", oid=oid, game="wsct", goal=22, trial=1)
        found = self.db.load_item(None)
        print("oid, gamer, found", oid, gamer, found)
        gamer = "trial=2"
        self.assertIn(str(gamer), page, f"oid {gamer} not in user {page}")

    def test_post_add_game(self):
        oid = self.db.insert(dict(name=357, year=5, gander="outro", age=12, games=()))
        user = self._post_add_game(oid)
        self.assertEqual(1, len(user[0]["games"]), f"oid {oid} not in user {user}")
        self.assertIn("'0'", str([gl["goal"] for gl in user[0]["games"]]), f"oid {oid} not in user {user}")
        user = self._post_add_game(oid, goal=33)
        self.assertIn("'33'", str([gl["goal"] for gl in user[0]["games"]]), f"oid {oid} not in user {user}")

    def test_post_user(self):
        user_data = dict(name=321, year=5, gander="outro", age=12, games=())
        response = self.fetch(r"/home/user", False, method="POST", body=json.dumps(user_data))
        self.assertEqual(200, response.code, "failed post_score")
        self.assertLess(5000, len(response.body), f"unexpected id size {response.body}")
        user = str(self.db.load_any()[0]["_id"])
        page = response.body.decode("utf8")
        # [print(u) for u in self.db.load_any()]
        self.assertIn(user, page, f"user {user} not in page {page}")

    def test_put_score(self):
        """Adiciona uma nova entrada de pontuação para o usuário 246 """
        oid = self.db.insert(dict(name=246, games=()))
        gamer = str(self.db.add_game(oid, 99))
        body = json.dumps(dict(_id=gamer, score=dict(marker=2460)))
        # body = json.dumps(dict(game=gamer, score=dict(marker=2460)))
        response = self.fetch(r"/record/store", False, method="PUT", body=body)
        self.assertEqual(200, response.code, "failed put_score")
        self.assertIn(gamer, str(response.body), "id do jogo não está no corpo")
        user = str(self.db.load_any())
        score = str(dict(marker=2460))
        oid = response.body.decode("utf8")
        self.assertIn(oid, user, f"oid {oid} not in user {user}")
        # [print(u) for u in self.db.load_any()]
        self.assertIn(score, user, f"oid {score} not in user {user}")


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
        # print('len(person), len(score), len(populate)', len(person), len(score), len(populate))
        # [print(sc[0]) for sc in populate]

        # [collection.update_one({'_id': ids}, {'$push': {'games.0.goals.0.trials.0.trial': item['_id']}}, upsert=True)
        [collection.update_one({'_id': ids}, {'$push': {f'games.{gamer}.score': item['_id']}}, upsert=True)
         for ids, items in populate for gamer, item in enumerate(items)]

        self.facade = Facade(db=collection)
        # print(self.facade.load_item(dict(_id=person[0])))

    def test_list_mongo(self):
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

    def test_add_user(self):
        self._init_mongo()
        oid = self.facade.insert(dict(name=321, games=()))
        gamer = self.facade.load_item(dict(_id=oid))
        as_str = "'name': 321, 'games': []"
        self.assertIn(as_str, str(gamer), f"found: {gamer}")
        self._add_game(oid)
        found = self.facade.expand_item(oid)
        fnd = str([fn for fn in found])
        games = "[{'game': 3, 'goal': 0, 'trial': 0, 'scorer': []}]"
        as_str = f"[{{'games': {games}, '_id': {{'_id': ObjectId('{str(oid)}'), 'name': 321}}}}]"
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

    def _add_game(self, person, game_id=3):
        scorer, _ = self.facade.add_game(person=person, game=game_id)  # dict(game=3, goals=())})
        gamer = self.facade.load_item(dict(_id=person))
        self.assertEqual(person, gamer["_id"], f"found gamer: {gamer}, person: {person}")
        as_str = "{'game': 3, 'goal': 0, 'trial': 0, 'scorer': [ObjectId('%s')]}" % scorer
        self.assertIn(as_str, str(gamer), f"found in games: {gamer['games']}")

    def test_add_game(self):
        self._init_mongo()
        person = self.person[0]
        self._add_game(person)
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


class TestWisconsinGame(unittest.TestCase):
    GO, OG = '../image/ok.png', '../image/cancel.png'

    def setUp(self) -> None:
        self.web = MagicMock()
        self.game = Wisconsin(self.web, 123456)
        self.db = MagicMock(name="db")
        self.game.next = lambda data: self.db.insert(score=data)

    def test_initial(self):
        self.assertEqual(0, self.game.categoria)
        self.assertEqual(1, self.game.carta_resposta.numeral)
        self.assertEqual(4, len(self.game.lista_carta_estimulo))
        self.assertEqual(127, len(self.game.lista_carta_resposta))
        self.assertIsInstance(self.game.card, MagicMock)
        self.assertEqual(1, self.game.card.binder.call_count)
        self.assertEqual(1, self.game.card.paint.call_count)
        self.assertEqual(0, self.game.card.resultado.call_count)

    def test_first_guess_wrong(self):
        carta0 = self.game.lista_carta_estimulo[3]
        self.assertIsInstance(carta0, Carta)
        carta0.do_click()
        self.assertEqual(1, self.web.resultado.call_count)
        self.assertEqual(1, self.game.outros_consecutivos)
        self.assertEqual(self.OG, self.web.resultado.call_args[0][0])
        self.assertEqual('Errado', self.web.resultado.call_args[0][1])
        self.assertEqual(1, self.db.insert.call_count)
        self.assertIn("valor", self.db.insert.call_args_list[0][1]["score"])
        self.assertFalse(any(self.db.insert.call_args_list[0][1]["score"]["valor"]))

    def test_three_first_guesses_wrong(self):
        cartas = self.game.lista_carta_estimulo
        [cartas[carta].do_click() for carta in (3, 1)]
        self.assertEqual(2, self.web.resultado.call_count)
        self.assertEqual(2, self.game.outros_consecutivos)
        cartas[2].do_click()
        self.assertEqual(self.OG, self.web.resultado.call_args.args[0])
        message = 'Errado. Clique a carta abaixo que combina com a mostrada em cima'
        self.assertEqual(message, self.web.resultado.call_args.args[1])
        self.assertEqual(3, self.db.insert.call_count)
        self.assertIn("ponto", self.db.insert.call_args_list[2][1]["score"])
        self.assertIn(3, self.db.insert.call_args_list[2][1]["score"]["ponto"])

    def test_ten_first_guesses_right(self):
        cartas = self.game.lista_carta_estimulo
        self._find_correct_answers()
        sequence_right = [go["cor"] for go in self.go[:10]]
        [cartas[carta].do_click() for carta in sequence_right[:-1]]
        self.assertEqual(9, self.web.resultado.call_count)
        cartas[2].do_click()
        self.assertEqual(self.GO, self.web.resultado.call_args.args[0])
        message = 'Certo'
        self.assertEqual(message, self.web.resultado.call_args.args[1][:5])
        self.assertIn("ponto", self.db.insert.call_args_list[9][1]["score"])
        self.assertIn(10, self.db.insert.call_args_list[9][1]["score"]["ponto"])
        cartas[3].do_click()
        self.assertEqual(self.OG, self.web.resultado.call_args.args[0])
        cartas[0].do_click()
        self.assertEqual(self.GO, self.web.resultado.call_args.args[0])

    def test_30_first_guesses_right(self):

        self.game.lista_categorias = self.game.lista_categorias[:3]
        cartas = self.game.lista_carta_estimulo
        self._find_correct_answers()
        self.ten_card_round("cor", 0)
        self.ten_card_round("forma", 10)
        self.ten_card_round("numero", 20, go=self.OG)
        self.assertEqual("Fim do Jogo", self.web.resultado.call_args.args[1])
        cartas[0].do_click()
        self.assertIn("carta", self.db.insert.call_args_list[29][1]["score"])
        self.assertIn(2, self.db.insert.call_args_list[29][1]["score"]["valor"][-1:])

    def ten_card_round(self, kind, card_count, go=None, count=None):
        go = go or self.GO
        cartas = self.game.lista_carta_estimulo
        end_count = card_count+10
        count = count or end_count
        sequence_right = [go[kind] for go in self.go[card_count:end_count]]
        [cartas[carta].do_click() for carta in sequence_right]
        self.assertEqual(count, self.web.resultado.call_count)
        self.assertEqual(go, self.web.resultado.call_args.args[0])

    def test_15_first_guesses_right(self):

        self.game.lista_carta_resposta = self.game.lista_carta_resposta[:15]
        cartas = self.game.lista_carta_estimulo
        self._find_correct_answers()
        self.ten_card_round("cor", 0)
        self.ten_card_round("forma", 10, go=self.OG, count=16)
        self.assertFalse(self.game.lista_carta_resposta)
        self.assertEqual("Fim do Jogo", self.web.resultado.call_args.args[1])
        cartas[0].do_click()

    def _find_correct_answers(self):
        lista = Wisconsin.LISTA
        keys = "numero forma cor".split()
        self.go = [{k: int(v)-1 if "n" in k else int(v) for k, v in zip(keys, nfc)} for nfc in lista]


if __name__ == '__main__':
    unittest.main()
