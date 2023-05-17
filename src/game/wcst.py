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

.. versionadded::    23.04
        Port to client interaction(05).

"""
from datetime import datetime

from browser import document, html
from collections import namedtuple as nt

COR = nt("Cor", "vm vd am az")(0, 1, 2, 3)
FOR = nt("For", "tri est cru cir")(0, 1, 2, 3)
COLORS = 'is-danger is-primary is-warning is-info'.split()
COLORN = 'verm verd amar azul'.split()
CLAZZ = {k: v for k, v in zip(COLORN, COLORS)}
FORM = {k: v for k, v in enumerate("play star cross circle".split())}


# FORM = {k: v for k, v in enumerate("triangulo estrela cruz circulo".split())}

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
        self._inicia(numero, forma, cor, jogo)

    def _inicia(self, numero, forma, cor, jogo):
        genero = 0 if forma not in [1, 2] else 1
        num = 0 if numero == 1 else 1
        self.jogo = jogo
        self.numeron = numero
        self.forman = forma
        self.colour = cor
        self.numero = self._numeros[numero - 1][genero]
        self.forma = self._formas[forma][num]
        self.cor = self._cores[cor][num][genero]

        self.num = numero
        self.img = self._formas[forma][2]
        # self.img = u"/static/plugins/wisconsin/images/%s.png" % self._formas[forma][2]
        self.color = self._cores[cor][2]

    def clicou(self, *_):
        self._click()

    def do_click(self, *_):
        self.jogo.click(self)

    def resultado(self, resultado, carta):
        carta = carta or self
        self._inicia(carta.numeron, carta.forman, carta.colour, carta.jogo)
        # acertou = self.testa_tudo_diferente(lista_cartas_resposta[0])
        resposta = document['carta_resposta']
        [resposta.classList.remove(CLAZZ[cor]) for cor in COLORN]
        # lista_cartas_resposta.pop(0)
        cor = carta.color[:4]
        resposta.classList.add(CLAZZ[cor])
        hero = document['carta_hero']
        hero.html = ''
        frm = carta.forman
        print(self.color[:4], cor, CLAZZ[cor], frm, carta.numeron)
        for figs in range(carta.numeron):
            fg = html.I(Class=f"fas fa-{carta.img} fa-2x is-size-2 has-text-black")
            form = html.SPAN(fg, Class="icon is-large") + html.BR()
            _ = hero <= form
        if not resultado:
            return
        if "Fim" in resultado:
            self._click = lambda *_: None
            print("O jogo terminou")
        if "Certo" in resultado:
            document["_resultado_"].html = resultado
            document["_icon_resultado_"].src = "../image/ok.png"
        else:
            document["_resultado_"].html = resultado
            document["_icon_resultado_"].src = "../image/cancel.png"

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


# listaCartasResposta = criaListaResposta()


########################################################################


class Wisconsin:
    def __init__(self):
        self.lista_carta_estimulo = self.cria_lista_estimulo()
        self.lista_carta_resposta = self.cria_lista_resposta()
        self.lista_categorias = ["cor", "forma"] #, "numero", "cor", "forma", "numero"]
        self.numCartasResposta = 64
        self.houses = dict()
        self.indica_carta_atual = self.categoria = self.acertos_consecutivos = self.outros_consecutivos = 0
        self._wisc = self

        self.carta_resposta = self.lista_carta_resposta.pop(0)
        self.carta_resposta.resultado('', None)
        for num, carta in enumerate(self.lista_carta_estimulo):
            document[f"carta_{num + 1}"].bind('click', carta.clicou)

    ########################################################################

    def cria_lista_resposta(self):
        """Cria a lista de cartas resposta. O conteúdo de cada item da lista é uma carta."""

        lista = ['101', '420', '203', '130', '411', '122', '403', '330', '421', '232',
                 '113', '300', '223', '112', '301', '433', '210', '332', '400', '132',
                 '213', '321', '212', '303', '410', '202', '323', '430', '211', '120',
                 '431', '110', '333', '422', '111', '402', '233', '312', '131', '423',
                 '100', '313', '432', '201', '310', '222', '133', '302', '221', '412',
                 '103', '311', '230', '401', '123', '331', '220', '102', '320', '231',
                 '423', '322', '200', '122']

        for indica in range(len(lista)):
            lista[indica] = Carta(numero=int(lista[indica][0]),
                                  forma=int(lista[indica][1]),
                                  cor=int(lista[indica][2]), jogo=self)
        # [print(f"cor {c.color}, form {c.forma}, num: {c.numero}") for c in lista[:20]]

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

        if carta_resposta.testa_mesma_categoria(carta_estimulo, self.lista_categorias[self.categoria]):
            self.acertos_consecutivos += 1
            resultado_teste = f"Certo {self.acertos_consecutivos}"
        else:
            self.acertos_consecutivos = 0
            resultado_teste = f"Errado td:{tudo_diferente} crc: {carta_resposta.color} cec: {carta.color}"

        if tudo_diferente:
            self.outros_consecutivos += 1
        else:
            self.outros_consecutivos = 0

        if self.outros_consecutivos == 3:
            self.outros_consecutivos = 0
            resultado_teste = "Errado. Clique a carta abaixo que combina com a mostrada em cima"
            # resultadoTeste = u"%s.<br/>Leia atentamente as instruções: %s" % (resultadoTeste, wcst.instrucoes_teste())

        # Grava a jogada no banco de dados
        table = [dict(
            carta_resposta=128-len(self.lista_carta_resposta),
            categoria=self.lista_categorias[self.categoria],
            acertos=self.acertos_consecutivos,
            # cor=carta_resposta.testa_mesma_categoria(carta_estimulo,
            #                                          self.lista_categorias[0]),
            # forma=carta_resposta.testa_mesma_categoria(carta_estimulo,
            #                                            self.lista_categorias[1]),
            # numero=carta_resposta.testa_mesma_categoria(carta_estimulo,
            #                                             self.lista_categorias[2]),
            outros=tudo_diferente,
            time=str(datetime.now()))]

        # Se os acertos consecutivos chegarem a 10, troca a categoria
        if self.acertos_consecutivos == 10:
            self.acertos_consecutivos = 0
            self.categoria += 1

        houses = {"indiceCartaAtual": self.indica_carta_atual,
                  "categoria": self.categoria,
                  "self.acertos_consecutivos": self.acertos_consecutivos,
                  "outrosConsecutivos": self.outros_consecutivos,
                  "wteste": None
                  }
        self._wisc.next(houses=houses, table=table)

        # Termina o teste se esgotar as categorias ou fim das cartas respostas.
        if ((self.categoria >= len(self.lista_categorias)) or
                (not self.lista_carta_resposta)):
            resultado_teste = "Fim do Jogo"
            self.carta_resposta.resultado(resultado_teste, None)
        else:
            nova_carta = self.lista_carta_resposta.pop(0)
            self.carta_resposta.resultado(resultado_teste, nova_carta)

        # self.redirect('/wisconsin/play?' + urllib.urlencode({"result": resultadoTeste.encode("UTF-8")}))
        return resultado_teste

    def next(self, houses, table):
        pass


def main():
    """Imprimi na tela as instruções do teste. """
    _ = Wisconsin()
