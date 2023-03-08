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
""" Activ REST API served by Tornado.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------
.. versionadded::    23.03
        test a rest api with tornado.
        add a fake persistence (03).

"""
import os

from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.ioloop import IOLoop
import json

# kanban = {"": ""}


class MainPage(RequestHandler):
    def get(self):
        self.render("kanban.html", titulo="Alite - Kanban", version="23.03")
        # self.write({'items': items})


class Kanban(RequestHandler):
    kanban = {"": ""}
    tasks = {"": ""}

    def get(self):
        # self.write({'items': items})
        with open("kbj.json", "r") as fjson:
            items = json.load(fjson)
            self.write(json.dumps(items))
        # self.write(json.dumps(Kanban.tasks))

    def post(self, *_):
        items = json.loads(self.request.body)
        Kanban.kanban = {att: val for att, val in items["KanbanModel"].items() if att != "tasks"}
        with open("kbj.json", "w") as fjson:
            json.dump(items, fjson)
        # print("kanban post", items)
        Kanban.tasks = items["KanbanModel"]["tasks"]
        self.write({'message': 'whole base saved'})


class TodoItem(RequestHandler):
    def post(self, id):
        Kanban.tasks[id] = json.loads(self.request.body)
        self.write({'message': 'new item added'})

    def delete(self, id):
        Kanban.tasks.pop(id) if id in Kanban.tasks else None
        self.write({'message': 'Item with id %s was deleted' % id})


def make_app():
    current_path = os.path.dirname(__file__)
    static_path = os.path.join(current_path, "..", "kanban")
    image_path = os.path.join(current_path, "image")
    print(static_path)

    urls = [
        ("/", MainPage),
        ("/api/load", Kanban),
        ("/api/save", Kanban),
        (r"/api/item", TodoItem),
        (r"/api/item/([^/]+)?", TodoItem),
        (r"/(.*\.py)", StaticFileHandler,  {'path': static_path}),
        (r"/image/(.*\.ico)", StaticFileHandler,  {'path': image_path}),
        (r"/image/(.*\.jpg)", StaticFileHandler,  {'path': image_path})
    ]
    return Application(
        urls, debug=True,
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=static_path
                       )


class HelloHandler(RequestHandler):
    def get(self):
        self.write({'message': 'hello world'})


def make_app_():
    urls = [("/", HelloHandler)]
    return Application(urls)


def start_server():
    from tornado.options import define, options

    define("port", default=8080, help="port to listen on")
    app = make_app()
    app.listen(options.port)
    print(f"listening on port {options.port}")
    IOLoop.instance().start()


if __name__ == '__main__':
    start_server()
