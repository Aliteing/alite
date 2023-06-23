#! /usr/bin/env python
# -*- coding: UTF8 -*-
""" Servidor web entregando o serviço em html.


Classes neste módulo:
    - :py:class:`BaseRequestHandler` Funções comuns para os gerentes de Chamada .
    - :py:class:`DefaultHandler`     Gerencia chamadas defeituosas.
    - :py:class:`HomeRequestHandler` Chamadas para a página inicial.
    - :py:class:`DashRequestHandler` Menu com os tipos de gráficos oferecidos.
    - :py:class:`PlotRequestHandler` Chamadas para a fachada de serviços.

Funções neste módulo:
    - :py:func:`make_server_app` Configura as rotas e parâmetros iniciais do servidor.
    - :py:func:`run_server` Executa o laço assíncrono do servidor.
    - :py:func:`main` Função principal que chama o run_server e make_server_app.

Changelog
---------

.. versionadded::    23.06
    |br| add :class:`HomeRequestHandler`,
    |br| :meth:`BaseRequestHandler.check_modal`, boiler and about (10)
    |br| :meth:`BaseRequestHandler.check_modal`, boiler and about (10)
    |br| :class:`PlotRequestHandler`, plot & dash, menu boiler review (23)


|   **Open Source Notification:** This file is part of open source program **Alite**
|   **Copyright © 2023  Carlo Oliveira** <carlo@nce.ufrj.br>,
|   **SPDX-License-Identifier:** `GNU General Public License v3.0 or later <http://is.gd/3Udt>`_.
|   `Labase <http://labase.selfip.org/>`_ - `NCE <http://portal.nce.ufrj.br>`_ - `UFRJ <https://ufrj.br/>`_.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

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
    """ Classe antecessora dos requests.
    """

    def initialize(
            self,
            service: RpcProxy(Cfg.dash_srv), config=None,
            status_code=404,
            message='Unknown Endpoint'
    ) -> None:
        """ Inicializa os requests.

        Declara um conjunto de parâmetros iniciais da chamada base.

        :param     service: Serviço rpc.
        :param      config: Configuração para os chamados.
        :param status_code: O estado para retornar no chamado.
        :param     message: Mensagem explicando o código de retorno.
        """
        self.service = service
        self.reason = message
        _ = status_code, config
        __version__ = Cfg.version
        self.version__ = Cfg.version
        self.about, self.help = "", ""

    def check_modal(self, op) -> None:
        """ Decide se tem que ligar ou desligar o painel modal.

        :param op: Operação recebida para ser avaliada.
        :return: Nenhum
        """
        self.about = "is-active" if op == "_" else ""

    def do_load(self, template=Cfg.BOIL_TPL, **kwargs: Any) -> None:
        """

        :param template: O arquivo de gabarito a ser usado.
        :param kwargs: Os parâmetros usados na geração do gabarito.
        :return: None
        """
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
    """ Captura as rotas defeituosas e apresenta a tela de erro.

    """
    def prepare(self):
        """ Captura as rotas defeituosas e apresenta a tela de erro.

        :return: None
        """
        # Use prepare() to handle all the HTTP methods
        self.set_status(404)
        self.render(Cfg.ERR_TPL, titulo="Alite - Erro 404", version=Cfg.version, about="")


class HomeRequestHandler(BaseRequestHandler):
    """ Captura chamadas para a página inicial.

    """

    async def get(self, op=None):
        """ Captura chamadas para a página inicial.

        :param op: Operação REST da requisição.
        :return: None
        """
        self.check_modal(op)
        """ Verifica se a operação pedida é transição do painel modal. """
        self.set_status(200)
        self.do_load()


class DashRequestHandler(BaseRequestHandler):
    """ Gerencia o menu para criar uma grade de opções

    """

    async def get(self, op=None, mid=None):
        """ Obtém images enviadas pelo dash_service retornando um gráfico pedido.

        :param op: Câmbio do estado do modal entre ativo e inativo
        :param mid: Tipo dos gráficos pedidos a ser enviado para o dash
        :return: (Um gabarito do painel com a lista de dados descritivos)
        """
        self.check_modal(op)
        _ = mid
        kind = "plot factor violin hist heat".split()
        icon = [(6, 5), (3, 2), (6, 0), (2, 2), (5, 4)]
        kind = list(zip(kind, kind, kind, icon))
        chart_menu = [
            [(a_chart, iy * -400 - 64, ix * -396, a_name, a_leg) for a_chart, a_name, a_leg, (ix, iy)
             in line_menu]
            for _, line_menu in enumerate([kind[:3], kind[3:]])
        ]
        self.set_status(200)
        self.do_load(Cfg.DASH_TPL, chart_menu=chart_menu)


class PlotRequestHandler(BaseRequestHandler):
    """ Manuseia requisições para o rpc dash_service

    """

    async def get(self, op=None, pid=None):
        """ Obtém images enviadas pelo dash_service retornando um gráfico pedido.

        :param op: Câmbio do estado do modal entre ativo e inativo
        :param pid: Tipo do gráfico pedido a ser enviado para o dash
        :return: (os dados da imagem codificados em base64)
        """
        def plot_pontos(cluster):
            return cluster.datascience_dash_service.plot_pontos()

        def plot_chart(cluster):
            return cluster.datascience_dash_service.plot_chart(pid)
        self.check_modal(op)
        kind = "plot factor violin hist heat".split()
        from nameko.standalone.rpc import ClusterRpcProxy
        # from dash.service import DashService
        # from nameko.testing.services import worker_factory
        # self.service = worker_factory(DashService)
        with ClusterRpcProxy(Cfg.config) as cluster_rpc:
            image = plot_chart(cluster_rpc) if pid in kind else plot_pontos(cluster_rpc)
        self.set_status(200)
        self.do_load(Cfg.PLOT_TPL, image=image)


def make_server_app(
        config: AnyStr,
        debug: bool
) -> Tuple[RpcProxy, Application]:
    service = RpcProxy(config)
    # get_games = r'/chart/(?P<id>[a-zA-Z0-9-]+)/?'
    app = Application(
        [
            (Cfg.GET_DASH, DashRequestHandler, dict(service=service, config=config)),
            (Cfg.GET_POINT, PlotRequestHandler, dict(service=service, config=config)),
            (Cfg.GET_GAMES, PlotRequestHandler, dict(service=service, config=config)),
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
