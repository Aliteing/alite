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
""" Game control server.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------
.. versionadded::    23.04
        open a user register window(05).

"""
import os

from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.ioloop import IOLoop
import json
from atlas_model import DS

# eica = {"": ""}


class MainPage(RequestHandler):
    def get(self):
        self.render("home.html", titulo="Alite - Games", version="23.04")
        # self.write({'items': items})


class Eica(RequestHandler):
    eica = {"": ""}
    tasks = {"": ""}

    def get(self):
        self.write(json.dumps(DS.load_all()))
        # self.write(json.dumps(Eica.tasks))

    def _get(self):
        # self.write({'items': items})
        with open("kbj.json", "r") as fjson:
            items = json.load(fjson)
            self.write(json.dumps(items))
        # self.write(json.dumps(Eica.tasks))

    def post(self, *_):
        items = json.loads(self.request.body)
        Eica.eica = {att: val for att, val in items.items() if att != "tasks"}
        # Eica.eica = {att: val for att, val in items["EicaModel"].items() if att != "tasks"}
        with open("kbj.json", "w") as fjson:
            json.dump(items, fjson)
        # print("eica post", items)
        # Eica.tasks = items["tasks"]
        self.write({'message': 'whole base saved'})


class Home(RequestHandler):

    def get(self):
        self.write(json.dumps(DS.load_all()))
        # self.write(json.dumps(Eica.tasks))

    def post(self, *_):
        # fields = json.loads(self.request.body)
        fields = self.request.arguments
        fields = {k: str(v[0], "utf8") for k, v in fields.items()}
        fields = json.dumps(fields)
        print("home post", fields)
        self.render("game.html", titulo="Alite - Games", version="23.04")

        # self.write({'message': 'whole registry saved'})


class EicaItem(RequestHandler):
    def post(self, oid):
        item = json.loads(self.request.body)
        Eica.tasks[oid] = item
        # print("TodoItem item", item)
        # DS.upsert(item)
        self.write({"message": f"new item {str(oid)} added or updated"})

    def delete(self, oid):
        Eica.tasks.pop(oid) if id in Eica.tasks else None
        self.write({'message': 'Item with id %s was deleted' % id})


def make_app():
    current_path = os.path.dirname(__file__)
    static_path = os.path.join(current_path, "..", "game")
    template_path = os.path.join(current_path, "templates")
    image_path = os.path.join(current_path, "image")
    print(static_path)

    urls = [
        ("/", MainPage),
        ("/api/load", Eica),
        ("/api/save", Eica),
        ("/home/save", Home),
        (r"/api/item", EicaItem),
        (r"/api/item/([^/]+)?", EicaItem),
        (r"/home/(.*\.py)", StaticFileHandler,  {'path': static_path}),
        (r"/(.*\.css)", StaticFileHandler,  {'path': template_path}),
        (r"/image/(.*\.ico)", StaticFileHandler,  {'path': image_path}),
        (r"/image/(.*\.jpg)", StaticFileHandler,  {'path': image_path})
    ]
    return Application(
        urls, debug=True,
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=static_path
                       )


def start_server():
    from tornado.options import define, options

    define("port", default=8080, help="port to listen on")
    app = make_app()
    app.listen(options.port)
    print(f"listening on port {options.port}")
    IOLoop.instance().start()


if __name__ == '__main__':
    start_server()
