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
""" Main eica client control.
Programa baseado no Teste Wisconsin
Autor: Neno Henrique Albernaz
Criado em Junho de 2008

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>
.. codeauthor:: Neno Henrique Albernaz<neno@nce.ufrj.br>
.. codeauthor:: Julia <carlo@nce.ufrj.br>

Changelog
---------
.. versionadded::    23.05
        add click from bazaar, need fix (16).
        win condition fixed, but allows crash (17).
        refactor WebCard out, new response card generation (18).
        add session and scoring conforming to API (19).

.. versionadded::    23.04
        Port to client interaction(05).

"""
from datetime import datetime

# from browser import document, html
from collections import namedtuple as nt

COR = nt("Cor", "vm vd am az")(0, 1, 2, 3)
FOR = nt("For", "tri est cru cir")(0, 1, 2, 3)
COLORS = 'is-danger is-primary is-warning is-info'.split()
COLORN = 'verm verd amar azul'.split()
CLAZZ = {k: v for k, v in zip(COLORN, COLORS)}
FORM = {k: v for k, v in enumerate("play star cross circle".split())}


########################################################################
class Carta:
    # Definição dos itens de uma carta.
    _numeros = [(u"Um", u"Uma"),
                (u"Dois", u"Duas"),
                (u"Três", u"Três"),
                (u"Quatro", u"Quatro")]
    _formas = [(u"Triângulo", u"Triângulos", "play"),
               (u"Estrela", u"Estrelas", "star"),
               (u"Cruz", u"Cruzes", "cross"),
               (u"Círculo", u"Círculos", "circle")]

    _cores = [((u"Vermelho", u"Vermelha"), (u"Vermelhos", u"Vermelhas"), "vermelho"),
              ((u"Verde", u"Verde"), (u"Verdes", u"Verdes"), "verde"),
              ((u"Amarelo", u"Amarela"), (u"Amarelos", u"Amarelas"), "amarelo"),
              ((u"Azul", u"Azul"), (u"Azuis", u"Azuis"), "azul")]

    _atributos = dict(numero='num', forma='img', cor='color')

    def __init__(self, numero, forma, cor, jogo):
        self._click = self.do_click
        self._resposta = jogo.card
        self._inicia(numero, forma, cor, jogo)

    def _inicia(self, numero, forma, cor, jogo):
        genero = 0 if forma not in [1, 2] else 1
        num = 0 if numero == 1 else 1
        self.jogo = jogo
        self.numeral = numero
        self.forman = forma
        self.colour = cor
        self.numero = self._numeros[numero - 1][genero]
        self.forma = self._formas[forma][num]
        self.cor = self._cores[cor][num][genero]

        self.num = numero
        self.img = self._formas[forma][2]
        self.color = self._cores[cor][2]

    def clicou(self, *_):
        self._click()

    def do_click(self, *_):
        self.jogo.click(self)

    def resultado(self, resultado, carta):
        resposta = self._resposta
        carta = carta or self
        self._inicia(carta.numeral, carta.forman, carta.colour, carta.jogo)
        cor = carta.color[:4]
        resposta.paint(color=CLAZZ[cor], form=FORM[carta.forman], number=carta.numeral)
        if not resultado:
            return
        if "Certo" in resultado:
            resposta.resultado("../image/ok.png", resultado)
        else:
            resposta.resultado("../image/cancel.png", resultado)

    def pega_atributos_carta(self):
        return u"%s %s %s" % (self.numero, self.forma, self.cor)

    def testa_mesma_categoria(self, outra_carta, categoria):
        """Testa se as cartas são iguais na categoria.
        Categoria pode ter atribuído três valores: numero, forma ou cor."""
        return (getattr(self, self._atributos[categoria]) ==
                getattr(outra_carta, self._atributos[categoria]))

    def testa_tudo_diferente(self, outra_carta):
        """Testa se as cartas diferem em todas as categorias."""
        for categoria in self._atributos:
            if self.testa_mesma_categoria(outra_carta, categoria):
                return False
        return True


########################################################################

def instrui_teste():
    """Imprime na tela as instruções do teste. """

    return u"""Este é um teste um pouco diferente, porque eu não posso lhe
    dizer muito a respeito do que fazer. Você vai ser solicitado a associar
    cada uma das cartas que vou te dar com uma dessas quatro cartas-chave
    mostradas na tela. Sempre selecione o link da carta-chave que você achar
    que combine com a carta que vou te dar. Eu não posso lhe dizer como
    associar as cartas, mas lhe direi, cada vez, se você está certo ou errado.
    Não há limite de tempo neste teste. Está Pronto? Vamos começar."""


########################################################################
class Wisconsin:
    LISTA = ['101', '420', '203', '130', '411', '122', '403', '330', '421', '232',
             '113', '300', '223', '112', '301', '433', '210', '332', '400', '132',
             '213', '321', '212', '303', '410', '202', '323', '430', '211', '120',
             '431', '110', '333', '422', '111', '402', '233', '312', '131', '423',
             '100', '313', '432', '201', '310', '222', '133', '302', '221', '412',
             '103', '311', '230', '401', '123', '331', '220', '102', '320', '231',
             '423', '322', '200', '122']

    def __init__(self, card, session):
        self._end_game = False
        self.card, self.session = card, session
        self.lista_carta_estimulo = self.cria_lista_estimulo()
        self.lista_carta_resposta = self.cria_lista_resposta()
        self.lista_categorias = ["cor", "forma", "numero", "cor", "forma", "numero"]
        self.numCartasResposta = 64
        self.houses = dict()
        self.indica_carta_atual = self.categoria = self.acertos_consecutivos = self.outros_consecutivos = 0
        self._wisc = self

        self.carta_resposta = self.lista_carta_resposta.pop(0)
        self.carta_resposta.resultado('', None)
        card.binder(self.lista_carta_estimulo)

    ########################################################################

    def cria_lista_resposta(self):
        """Cria a lista de cartas resposta. O conteúdo de cada item da lista é uma carta."""

        lista = [Carta(numero=int(n), forma=int(f), cor=int(c), jogo=self) for n, f, c in self.LISTA]

        return 2 * lista

    ########################################################################

    def cria_lista_estimulo(self):
        """Cria a lista de cartas estimulo. O conteúdo de cada item da lista é uma carta.
        """
        return [Carta(1, FOR.tri, COR.vm, self),
                Carta(2, FOR.est, COR.vd, self),
                Carta(3, FOR.cru, COR.am, self),
                Carta(4, FOR.cir, COR.az, self)]

    def click(self, carta, *_):
        carta_resposta = self.carta_resposta
        carta_estimulo = carta
        # print(carta_resposta.color, carta.color, self.lista_categorias[self.categoria])

        tudo_diferente = carta_resposta.testa_tudo_diferente(carta_estimulo)
        if self._end_game:
            return

        if carta_resposta.testa_mesma_categoria(carta_estimulo, self.lista_categorias[self.categoria]):
            self.acertos_consecutivos += 1
            resultado_teste = f"Certo {self.acertos_consecutivos}"
        else:
            self.acertos_consecutivos = 0
            resultado_teste = f"Errado"
            # resultado_teste = f"Errado {tudo_diferente}"
            # resultado_teste = f"Errado td:{tudo_diferente} crc: {carta_resposta.color} cec: {carta.color}"

        if tudo_diferente:
            self.outros_consecutivos += 1
        else:
            self.outros_consecutivos = 0
        val = [1 if carta_resposta.testa_mesma_categoria(carta_estimulo, a) else 0 for a in "cor forma numero".split()]
        data = dict(
            _id=self.session,
            carta=128-len(self.lista_carta_resposta),
            casa=carta_estimulo.pega_atributos_carta(),
            move=carta_resposta.pega_atributos_carta(),
            ponto=(self.acertos_consecutivos, self.outros_consecutivos, tudo_diferente),
            valor=val + [self.categoria],
            time=str(datetime.now())
        )

        if self.outros_consecutivos == 3:
            self.outros_consecutivos = 0
            resultado_teste = "Errado. Clique a carta abaixo que combina com a mostrada em cima"

        # Se os acertos consecutivos chegarem a 10, troca a categoria
        if self.acertos_consecutivos == 10:
            self.acertos_consecutivos = 0
            self.categoria += 1
        self._wisc.next(data)

        # Termina o teste se esgotar as categorias ou fim das cartas respostas.
        if ((self.categoria >= len(self.lista_categorias)) or
                (not self.lista_carta_resposta)):
            resultado_teste = "Fim do Jogo"
            self.carta_resposta.resultado(resultado_teste, None)
            self._end_game = True

        else:
            nova_carta = self.lista_carta_resposta.pop(0)
            if not self.lista_carta_resposta:
                resultado_teste = "Fim do Jogo"
            self.carta_resposta.resultado(resultado_teste, nova_carta)
        return resultado_teste

    def next(self, data):
        self.card.send(data)


def main(document, html, ajax, session):
    """Imprimi na tela as instruções do teste. """

    class WebCard:
        def __init__(self, oid='carta_resposta'):
            self.hero, self.doc = document['carta_hero'], document[oid]
            self.resposta, self.icon = document["_resultado_"], document["_icon_resultado_"]

        def paint(self, color, form, number):
            [self.doc.classList.remove(cor) for cor in 'is-danger is-primary is-warning is-info'.split()]
            self.doc.classList.add(color)
            self.hero.html = ''
            icon = f"fas fa-{form} fa-2x is-size-2 has-text-black"
            _ = [self.hero <= (html.SPAN(html.I(Class=icon), Class="icon is-large") + html.BR()) for _ in range(number)]

        def resultado(self, icon, text):
            self.resposta.html = text
            self.icon.src = icon

        @staticmethod
        def send(data, url=r"/record/store", action=lambda t: None, method="PUT"):
            def on_complete(request):
                if int(request.status) == 200 or request.status == 0:
                    # print("req = ajax()== 200", request.text)
                    action(request.text)
                else:
                    print("error " + request.text)

            req = ajax.ajax()
            req.bind('complete', on_complete)
            # url = "/record/" + operation
            req.open(method, url, True)
            # req.set_header('content-type', 'application/x-www-form-urlencoded')
            req.set_header("content-type", "application/json")
            # req.set_header("Content-Type", "application/json; charset=utf-8")
            import json
            data = json.dumps(data)
            print("def send", data)
            req.send(data)

        @staticmethod
        def binder(cartas):
            [document[f"carta_{num + 1}"].bind('click', carta.clicou) for num, carta in enumerate(cartas)]

    _ = Wisconsin(WebCard(), session)
