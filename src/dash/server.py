#! /usr/bin/env python
# -*- coding: UTF8 -*-
""" Servidor web entregando o serviço em html.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------
.. versionadded::    23.06
        first version of main (09)
        add homepage, boiler and about (10)

    This file is part of  program Alite
    Copyright © 2023  Carlo Oliveira <carlo@nce.ufrj.br>,
    `Labase <http://labase.selfip.org/>`_ - `NCE <http://portal.nce.ufrj.br>`_ - `UFRJ <https://ufrj.br/>`_.
    SPDX-License-Identifier: `GNU General Public License v3.0 or later <http://is.gd/3Udt>`_.

"""
import tornado.template
from tornado.options import define, options
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler, StaticFileHandler
from nameko.rpc import RpcProxy
from typing import Any, Tuple, AnyStr
from dash import Configuration as Cfg

# tornado.template.execute(about=lambda *_: "")
version__ = Cfg.version


# noinspection PyAttributeOutsideInit
class BaseRequestHandler(RequestHandler):
    def initialize(
            self,
            service: RpcProxy(Cfg.dash_srv), config=None,
            status_code=404,
            message='Unknown Endpoint'
    ) -> None:
        self.service = service
        self.reason = message
        _ = status_code, config
        __version__ = Cfg.version
        self.version__ = Cfg.version
        self.about, self.help = "", ""

    def check_modal(self, op) -> None:
        self.about = "is-active" if op == "_" else ""

    def do_load(self, template=Cfg.BOIL_TPL, **kwargs: Any) -> None:
        template_ = tornado.template.Loader(Cfg.tpl)
        self.finish(template_.load(template).generate(
            version=Cfg.version, about=self.about, help=self.help, **kwargs))

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        self.set_header(
            'Content-Type', 'application/json; charset=UTF-8'
        )
        body = {
            'method': self.request.method,
            'uri': self.request.path,
            'code': status_code,
            'message': self._reason
        }
        self.finish(body)


class DefaultHandler(RequestHandler):
    def prepare(self):
        # Use prepare() to handle all the HTTP methods
        self.set_status(404)
        self.render(Cfg.ERR_TPL, titulo="Alite - Erro 404", version=Cfg.version, about="")


class HomeRequestHandler(BaseRequestHandler):

    async def get(self, op=None):
        self.check_modal(op)
        self.set_status(200)
        self.do_load()


class DashRequestHandler(BaseRequestHandler):

    async def get(self, op=None):
        self.check_modal(op)
        from nameko.standalone.rpc import ClusterRpcProxy
        # from dash.service import DashService
        # from nameko.testing.services import worker_factory
        # self.service = worker_factory(DashService)
        with ClusterRpcProxy(Cfg.config) as cluster_rpc:
            image = cluster_rpc.datascience_dash_service.plot_pontos()
        self.set_status(200)
        self.do_load(Cfg.DASH_TPL, image=image)


def make_server_app(
        config: AnyStr,
        debug: bool
) -> Tuple[RpcProxy, Application]:
    service = RpcProxy(config)
    app = Application(
        [
            (Cfg.GET_POINT, DashRequestHandler, dict(service=service, config=config)),
            (Cfg.GET_GAMES, DashRequestHandler, dict(service=service, config=config)),
            (r"/(.?)", HomeRequestHandler, dict(service=service, config=config)),
            (Cfg.STT_PATH, StaticFileHandler, {'path': Cfg.img}),
            (Cfg.CSS_PATH, StaticFileHandler, {'path': Cfg.css}),
        ],
        compress_response=True,
        serve_traceback=debug,
        default_handler_class=DefaultHandler,
        debug=True,
        template_path=Cfg.tpl,
    )
    return service, app


define('port', default=Cfg.port, help='port to listen on')


def run_server(app: tornado.web.Application, port: int):
    _port = int(options.port or port)
    http_server = HTTPServer(app)
    http_server.listen(_port)
    print('Listening on http://localhost:%i' % _port)
    IOLoop.current().start()


def main(args=Cfg):
    addr_service, dash_app = make_server_app(config=args.dash_srv, debug=args.debug)
    run_server(app=dash_app, port=args.port,)


if __name__ == '__main__':
    main()
