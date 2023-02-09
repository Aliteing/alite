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
"""Inter face persistence with Activ REST API.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------
.. versionadded::    23.02
        test connection with activ.

"""
import mechanize
# from BeautifulSoup import BeautifulSoup as soup
import ssl
import json
from urllib import request, parse
DATA = """<html><body><pre>
{
  "task":{
    "id":"02",
    "desc": "oi"
  }
}
</pre></body></html>"""
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
# ssl_version corrections are done


class ActivPainter:
    def __init__(self):
        self._data = dict()
        self._page = "/rest/wiki/edit/labase/_Alite_kanban_LABASE"

    def read(self):
        print(self._page)
        kanban = request.urlopen(self._page)
        print(kanban)
        if isinstance(kanban, tuple):
            kanban = kanban[0]
            self._data = kanban.read()
        else:
            self._data = kanban.read()  # .decode('utf8')
        print(self._data)
        jkb = json.loads(str(self._data))
        self._data = jkb["result"]
        # print(jkb["result"]["wikidata"]["conteudo"])
        chtml = jkb["result"]["conteudo"]["value"]
        print(chtml)

    def write(self):
        from browser import ajax
        page = "/rest/wiki/edit/labase/_Alite_kanban_LABASE"
        form = dict(
            action="",
            nomepag=dict(type="@hidden", value=self._data["nomepag"]),
            revision=dict(type="@hidden", value=self._data["revision"]),
            tags=dict(type="@text", value=self._data["tags"]),
            e_usuario=dict(type="@text", value=True),
            e_owner=dict(type="@text", value=True),
            conteudo=dict(type="@textarea", value=DATA)
        )
        # self.write(dict(status=0, result=form))
        print(self._data)
        data = parse.urlencode(form).encode()
        req = ajax.Ajax()
        # req.bind('complete', on_complete)
        # send a POST request to the url
        req.open('POST', page, True)
        req.set_header('content-type', 'application/x-www-form-urlencoded')
        # send data as a dictionary
        resp = req.send(form)
        # req = request.Request(page, data=data)  # this will make the method "POST"
        # resp = request.urlopen(req)
        print(resp)


def scrap_from_page():
    # self.page='https://activufrj.nce.ufrj.br/evaluation/result/Neuro_UM_XII'
    plat = "https://activufrj.nce.ufrj.br"
    page = "/rest/wiki/edit/labase/_Alite_kanban_LABASE"
    mech = mechanize.Browser()
    mech.set_handle_robots(False)
    mech.open(plat)

    mech.select_form(nr=0)
    mech["user"] = "carlo"
    mech["passwd"] = "labase4ct1v"
    mech.submit().read()
    print(plat+page)
    # soup(results)
    kbf = mech.open(plat + page)
    kanban = kbf.read()
    # print(kbf.result)
    mech.viewing_html()
    jkb = json.loads(kanban)["result"]
    print("kanban", jkb["nomepag"])  # )
    # print(jkb["result"]["wikidata"]["conteudo"])
    print(jkb["conteudo"]["value"])


if __name__ == '__main__':
    # scrap_from_page()
    scrap_from_page()
