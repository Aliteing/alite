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
"""Module a Kanban board with task tickets.

.. codeauthor:: Pedro Rodriguez <pedro.rodriguez.web @ gmail.com>
.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

Changelog
---------
.. versionadded::    23.02
        initial modifications from original code.
        added board label with current task timing.
        remove delete button from task.
        add several properties and icons to task (14).
        change to pastel palette and introduce facets (15).
        propose save with JSON, add svg icons (16).

.. versionadded::    23.03
        improve JSON representation (01).
        moved tag insertion to init demo (02).
        add class Board instead of plain root (02).
        fix KanbanModel to use Board (03).
        adjust load and save to match mongo JSON (08).
        add tasks to server and database (09).
        tags and date parsing from cli (16).
        datetime to and fro str for JSON comply (22).
        popup dialog for tags edit, just demo (22).
        retrieve and print new values from popup (23).
        fix move sending task origin and destination to db (27).
        menu names and move tag dialog to tags entry (27).
        change tags dialog to bulma, start menus (28).
        menu popup test working, need selected (30).
        review task colors, add tags modal (31).

"""
# ----------------------------------------------------------
import time
from browser import document as doc
from browser import confirm, prompt, alert, svg, window, ajax, bind
from browser.local_storage import storage
import browser.html as html
from collections import namedtuple
import json

# ----------------------------------------------------------
IcoColor = namedtuple("IcoColor", "name icon color")
SCHEMA_REVISION = "1.0"
LABASE = "LABASE"
STEPS = [
    "REPOSITÓRIO", "PENDENTES", "PLANEJANDO", "DESPACHO", "EXECUTANDO", "TERMINADA"
]

STEPS_COLORS = (
    "#777777", "#888888", "#999999", "#AAAAAA", "#BBBBBB", "#CCCCCC", "#DDDDDD", "#EEEEEE", "#FFFFFFF"
)

_TASKS_COLORS = [
    "#EE0000", "#00CC00", "#0088EE", "#EEEE00", "#EEA500"
]
TASKY_COLORS = tuple("LightCyan LightGray BurlyWood PeachPuff LightSalmon Salmon LightPink DarkOrange Red"
                     " Yellow PaleGreen GreenYellow"
                     " PowderBlue Aquamarine DeepSkyBlue DodgerBlue MediumOrchid RosyBrown plum orchid".split())
TASKS_COLORS = tuple("LightCyan LemonChiffon PaleGreen PowderBlue Aquamarine"
                     " LightSalmon LightPink Orchid PeachPuff Plum"
                     " LightGray Yellow  GreenYellow DeepSkyBlue DodgerBlue"
                     " Salmon Red MediumOrchid DarkOrange BurlyWood".split())

FACET_COLOR_ = F_ = "darkred darkorange peach gold darkgreen navy" \
                    " indigo purple deeppink brown".split()

FACET_COLORS = FC = "tomato HotPink violet LightSteelBlue CornFlowerBlue PaleTurquoise" \
                    " DarkSeaGreen DarkKhaki coral SandyBrown".split()

TIME_FMT = "%Y/%m/%d %H:%M:%S"

DIAL = [f"dial-{pos if pos != '_' else ''}" for pos in "off min low med-low med _ high max".split()]
BATT = [f"battery-{pos if pos != '_' else ''}" for pos in "empty quarter half three-quarters full".split()]
_FACET = dict(
    level=dict(
        _self=f"gauge {FC[0]}",
        cloud="cloud ivory", kite="dove cyan", ship="ship green", fish="fish navy", crab="shrimp red"),
    phase=dict(
        _self=f"timeline  {FC[1]}", inception="brain purple", elaboration="ruler cyan",
        construction="hammer green", review="eye yellow", transition="truck-fast red"),
    develop=dict(
        _self=f"develop  {FC[2]}", spike="road-spikes purple", feature="box cyan", enhancement="ribbon green",
        refactor="industry blue", bugfix="bug red"),
    text=dict(
        _self=f"book  {FC[3]}", document="pen purple", tutorial="graduation-cap blue", manual="book-open green",
        report="book-open-reader orange", project="list-check red"),
    nature=dict(
        _self=f"book  {FC[4]}", development="building magenta", info="database cyan", engineering="gears Chartreuse",
        research="book-atlas yellow", science="vial red"),
    work=dict(
        _self=f"person  {FC[5]}", planning="pen-ruler purple", activity="person-digging cyan",
        meeting="people-group green", session="users yellow", exam="microscope red"),
    scope=dict(
        _self=f"stethoscope  {FC[6]}", pace="shoe-prints salmon", story="dragon cyan", epic="shield green",
        milestone="bullseye orange", release="truck yellow"),
    cost=dict(
        _self=f"wallet  {FC[7]}", farthing="crow salmon", penny="dog cyan", shilling="horse green",
        crown="crown orange", libra="chess-king yellow"),
    # cost=dict(
    #     _self=f"wallet  {FC[7]}", farthing="_one_cent purple", penny="coins cyan", shilling="sun green",
    #     crown="crown yellow", pound="money-bill red"),
    risk=dict(
        _self=f"radiation  {FC[8]}", low="circle-radiation purple", ordinary="biohazard cyan", medium="fire green",
        high="bomb yellow", extreme="explosion salmon"),
    value=dict(
        _self=f"heart  {FC[9]}", common="spray-can-sparkles salmon", unusual="hand-sparkles cyan",
        rare="star-half-stroke green", legendary="star orange", mythical="wand-sparkles yellow"),
)


# FACET = {fk: {tk: IcoColor(*tv.split()) for tk, tv in fv.items()} for fk, fv in _FACET.items()}


# ----------------------------------------------------------
class KanbanException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, f"Kanban Error: {msg}")


# ----------------------------------------------------------
class KanbanModel:
    NEW = True

    def __init__(self, counter=1, schema_revision=None, steps_colors=(),
                 tasks_colors=(), tasks=None):
        self.schema_revision = schema_revision
        self._counter = int(counter)
        self._steps_colors = list(steps_colors)
        self._tasks_colors = list(tasks_colors)
        self.tasks = {"": Task()}

        if tasks is None:
            self.board = Board(counter=self._counter, schema_revision=schema_revision, steps_colors=steps_colors,
                               tasks_colors=tasks_colors)
            task: Task = self.board
            self.tasks = {"board": task}
            # self.tasks = {"root": self.board}
        else:
            # self.board = Board(**(tasks["board"]["Board"]))
            self.board = Board(**(tasks["board"]))
            # self.board = Board(**(tasks["root"]["Board"]))
            # tasks.pop("board")
            # tasks.pop("root")
            # self.tasks = [Task(**(tsk["Task"])) for tsk in tasks if isinstance(tsk, dict)]
            self.tasks = {tsk_id: Task(**tsk) for tsk_id, tsk in tasks.items() if isinstance(tsk, dict)
                          and tsk_id != "board"} if isinstance(tasks, dict) else {"board": self.board}
            # self.tasks = {tsk_id: Task(**(tsk["Task"])) for tsk_id, tsk in tasks["tasks"].items()
            #               if isinstance(tsk, dict)
            #               and "Task" in tsk} if isinstance(tasks, dict) else {"board": self.board}
        # print("got tasks ok>>>> ", self.board.task_ids)
        # [print(tsk, a_tsk) for tsk, a_tsk in tasks["tasks"].items()] if isinstance(tasks, dict) else print("no tasks")

    @property
    def steps_colors(self):
        return self.board.steps_colors

    @property
    def tasks_colors(self):
        return self.board.tasks_colors

    def add_step(self, desc, color_id):
        step = self.add_task("board", desc, color_id, 0, prefix="step{}")
        self.board.add_task(step)
        return step
        # return self.add_task("board", desc, color_id, 0, prefix="step{}")
        # return self.add_task("root", desc, color_id, 0, prefix="step{}")

    def add_task(self, parent_id, desc, color_id, progress, prefix="task{}"):
        task_id = self.get_next_id(prefix)
        task = Task(task_id, 0, desc, color_id, progress)
        # print("task.oid", task.oid, "self.tasks", self.tasks)
        self.tasks[task.oid] = task

        parent_task = self.tasks[parent_id]
        parent_task.add_task(task)

        return task

    def remove_task(self, task_id):
        task = self.tasks[task_id]
        for sub_task_id in list(task.task_ids):
            self.remove_task(sub_task_id)

        parent_task = self.tasks[task.parent_id]
        del self.tasks[task_id]
        parent_task.remove_task(task)

    def move_task(self, task_id, dst_task_id):
        task = self.tasks[task_id]

        parent_task = self.tasks[task.parent_id]
        parent_task.remove_task(task)

        dst_task = self.tasks[dst_task_id]
        dst_task.add_task(task)
        return task, parent_task, dst_task

    def get_next_id(self, prefix):
        next_id = prefix.format(self.board.counter)
        self.board.counter += 1
        return next_id

    def __repr__(self):
        # return json_repr(self)
        rep = json_repr(self.tasks)
        rep.update(dict(board=json_repr(self.board)))
        return rep


# ----------------------------------------------------------
class Task:
    def __init__(self, oid="", parent_id=None, desc=None, color_id=0, progress=0, _id=0,
                 task_ids=(), tags=(), users=(), calendar=(), comments=(), external_links=()):
        self._id = str(_id)
        self.oid = oid
        self.parent_id = parent_id
        self.desc = desc
        self.color_id = int(color_id)
        self.progress = int(progress)
        self.task_ids = list(task_ids)
        self.tags = list(tags)
        self.users = list(users)
        self.calendar = list(calendar)
        self.comments = list(comments)
        self.external_links = list(external_links)

    def upsert(self, tags=(), users=(), calendar=(), comments=(), external_links=()):
        def to_fro_dict(argument, attribute):
            _tags = {k: v for k, v in attribute}
            _tags.update(argument)
            attribute = list(_tags.items())
            return attribute

        pairing = zip([tags, users, calendar, comments, external_links],
                      [self.tags, self.users, self.calendar, self.comments, self.external_links])
        _ = [to_fro_dict(argument, attribute) for argument, attribute in pairing]

    def add_task(self, task):
        self.task_ids.append(task.oid)
        task.parent_id = self.oid

    def remove_task(self, task):
        self.task_ids.remove(task.oid)
        task.parent_id = None

    def existing_extras(self):
        extras = [self.tags, self.users, self.calendar, self.comments, self.external_links]
        names = "self tags users calendar comments external_links".split()
        return [icon for icon, count in zip(names, extras) if count]

    def __repr__(self):
        return json_repr(self)


# ----------------------------------------------------------
class Board(Task):
    def __init__(self, oid=LABASE, parent_id=None, counter=1, schema_revision=SCHEMA_REVISION, _id=0,
                 steps_colors=STEPS_COLORS, tasks_colors=TASKS_COLORS, task_ids=(), current=None, desc=None):
        super().__init__(oid=oid, parent_id=parent_id, task_ids=task_ids, desc=desc, _id=_id)
        self._id = _id

        self.schema_revision = schema_revision
        self.counter = int(counter)
        self.steps_colors = list(steps_colors)
        self.tasks_colors = TASKS_COLORS or list(tasks_colors)
        self.current = current


# ----------------------------------------------------------
class KanbanBoard:
    def __init__(self, kanban):
        self.kanban = kanban
        control = "play pause stop".split()
        self.board_name = "LABASE"
        self.board_span = html.SPAN(self.board_name + "&nbsp;&nbsp;&nbsp;", Id="_control_board_name")
        self.external_link = html.SPAN(Id="_external_link", Class="fa fa-external-link")
        self.menu = html.SPAN(Id="_icon_menu", Class="fa fa-bars")
        self.controls = [html.SPAN("&nbsp;", Id=f"_control_{ico}", Class=f"fa-solid fa-{ico}") for ico in control]
        self.board = doc["board"]
        self.task_name = ""
        self.task_span = html.SPAN(self.task_name, Id="_control_task_name")
        self.timeline = html.DIV(id="task_deadline", Class="time_bar")

    def draw_deadline(self, base, width=50):
        _ = self
        node = html.DIV(id="task_deadline", Class="time_bar")
        node.style.width = percent(width)
        node.style.backgroundColor = "blue"
        _ = base <= node
        return node

    def draw_timeline(self, base, width=1):
        node = self.timeline
        node.style.width = percent(width)
        node.style.backgroundColor = "lightgray"
        _ = base <= node
        return node

    def draw(self, step_ids):
        _ = self
        width = 100 / len(step_ids)
        board = doc["board"]
        node = html.DIV("&nbsp;&nbsp;&nbsp;", id="project_board", Class="step_header")
        _ = node <= self.external_link
        _ = node <= self.board_span
        controls = self.controls
        _ = [node <= control for control in controls]
        _ = [control.bind("click", handler)
             for control, handler in zip(controls, [self.start_task, self.pause_task, self.stop_task])]
        _ = node <= self.task_span
        node.style.width = percent(5 * width + 1)
        node.style.backgroundColor = "ivory"
        _ = board <= node
        bar = self.draw_deadline(base=node)
        self.draw_timeline(base=bar)
        node.bind('dragover', self.drag_over)
        node.bind('drop', self.drag_drop)

    def drag_over(self, ev):
        _ = self
        ev.preventDefault()

        ev.data.dropEffect = 'move'

    def drag_drop(self, ev):
        ev.preventDefault()
        ev.stopPropagation()

        task_id = ev.data['text']
        task = self.kanban.tasks[task_id].desc
        self.task_span.text = task

    def start_task(self, *_):
        self.timeline.width = 10
        self.timeline.style.backgroundColor = "lightgray"

    def pause_task(self, *_):
        self.timeline.style.backgroundColor = "purple"

    def stop_task(self, *_):
        from activ_painter import ActivPainter
        ap = ActivPainter()
        ap.read()
        ap.write()
        self.timeline.style.backgroundColor = "lightgray"
        self.timeline.width = 1


# ----------------------------------------------------------
class KanbanView:
    def __init__(self, kanban):
        self.new = True
        self.kanban = kanban
        self.board = KanbanBoard(kanban)
        self.board.external_link.bind('click', self.write)
        # doc['load_kanban'].bind('click', self.load)
        # doc['save_kanban'].bind('click', self.save)
        # doc['dump'].bind('click', self.dump)
        # self.init_model() if self.new else None

    @staticmethod
    def parse_desc(desc, tsk):
        import datetime
        import re
        now = datetime.datetime.now()
        dtd = datetime.timedelta
        dd, ww, hh = lambda dt: dtd(days=dt), lambda dt: dtd(weeks=dt), lambda dt: dtd(hours=dt)

        def insert_unique(argument, key, value):
            as_dict = dict(argument)
            as_dict.update([(key, value)])
            return list(as_dict.items())

        def do_at(txt):
            txt, time_lapse = int(txt[:-1]), txt[-1].lower()
            at_parse = dict(
                d=lambda t=txt: str(now + dd(t)), w=lambda t=txt: str(now + ww(t)), h=lambda t=txt: str(now + hh(t)))
            tsk.calendar = insert_unique(tsk.calendar, "due", at_parse[time_lapse]())

        def do_hash(txt):
            key, value = txt.split(":")
            _key = {facet[0]: facet for facet in _FACET}[key]
            value = {facet[0]: facet for facet in _FACET[_key]}[value]
            tsk.tags = insert_unique(tsk.tags, _key, value)

        def do_pct(txt):
            tsk.progress = int(txt)

        def do_amp(txt):
            tsk.users = insert_unique(tsk.users, txt, 0)

        def do_exc(txt):
            tsk.external_links = insert_unique(tsk.external_links, txt, 0)

        def do_mark(arg, mrk):
            _args = re.findall(f" {arg}(\S*)", desc)
            try:
                [mrk(ag) for ag in _args]
            except ValueError as err:
                print("errValueError", err)
                pass
            except KeyError as err:
                print("errKeyError", err)
                pass
            except AttributeError as err:
                print("errAttributeError", err)
                pass
            except IndexError as err:
                print("errIndexError", err)
                pass
            # print(f"arg {arg}", _args, mrk)
            return _args

        mark = "@#%&!"
        _ = [do_mark(arg, mrk) for arg, mrk in zip(mark, [do_at, do_hash, do_pct, do_amp, do_exc])]
        rex = f" [{mark}]\S*"
        desc_sub = re.sub(rex, "", desc)

        tsk.desc = desc_sub
        # zip(mark, [tsk.calendar, tsk.tags, tsk.progress, tsk.users, tsk.external_links])]

    def write(self, page="/api/save", item=None, *_):
        _item = item or self.kanban

        txt = json.dumps(repr(_item))
        # print(txt)
        # data = parse.urlencode(txt).encode()
        data = txt

        def on_complete(_req):
            if _req.status == 200 or req.status == 0:
                print("complete ok>>>> " + _req.text)
            else:
                print("error detected>>>> " + _req.text)

        req = ajax.Ajax()
        req.bind('complete', on_complete)
        req.open('POST', page, True)
        # req.set_header('content-type', 'application/x-www-form-urlencoded')
        req.set_header('content-type', 'application/json')
        req.send(data)
        # print(resp)

    def read(self, *_):
        def on_complete(_req):
            if _req.status == 200 or req.status == 0:
                text = _req.text.replace("pound", "libra")
                _rt = json.loads(text)
                # print(_rt)
                self.kanban = KanbanModel(tasks=_rt)
                [self.parse_desc(t.desc, t) for t in self.kanban.tasks.values()]
                # self.kanban = KanbanModel(tasks=json.loads(_req.text)["KanbanModel"])
                # task20 = self.kanban.tasks["task20"]
                # print(str(task20))
                # task20.task_ids.append("task36")
                self.draw()

                print("complete ok>>>> ")  # + _req.text)
            else:
                print("error detected>>>> " + _req.text)

        page = "/api/load"

        req = ajax.Ajax()
        req.bind('complete', on_complete)
        req.open('GET', page, True)
        # req.set_header('content-type', 'application/x-www-form-urlencoded')
        req.set_header('content-type', 'application/json')
        req.send()

    @staticmethod
    def create_script_tag(src="icons.svg"):
        import urllib.request
        _fp = urllib.request.urlopen(src)
        _data = _fp.read()
        _tag = doc["_money_"]
        _tag.html = _data
        return _tag

    def draw(self):
        doc.body.style.backgroundImage = "url(https://wallpaperaccess.com/full/36356.jpg)"
        # self.create_script_tag()
        # step_ids = self.kanban.tasks["board"].task_ids
        step_ids = self.kanban.board.task_ids
        # print(step_ids)
        # step_ids = self.kanban.tasks["board"].task_ids
        width = 100 / len(step_ids)
        board = doc["board"]
        clear_node(board)
        self.board.draw(step_ids)
        for step_id in step_ids:
            step = self.kanban.tasks[step_id]
            self.draw_step(step, width, board)

    def draw_step(self, step, width, board):
        node = html.DIV(id=step.oid, Class="step")
        node.style.width = percent(width)
        # node.style.backgroundColor = self.kanban.steps_colors[step.color_id]
        rgb = int(f"0x{self.kanban.steps_colors[step.color_id][-2:]}", 16)
        node.style.backgroundColor = f"rgba({rgb},{rgb},{rgb},0.3)"
        _ = board <= node

        header = html.DIV(Class="step_header")
        _ = node <= header

        title = html.PRE(step.desc, Class="step_title")
        _ = header <= title

        count = html.PRE(0, id=f"{step.oid} count", Class="step_count")
        count.text = len(step.task_ids)
        _ = header <= count

        node.bind('dragover', self.drag_over)
        node.bind('drop', ev_callback(self.drag_drop, step))

        title.bind('click', ev_callback(self.add_task, step, node))

        self.draw_tasks(step, node)

    def draw_tasks(self, parent_task, parent_node):
        for task_id in parent_task.task_ids:
            task = self.kanban.tasks[task_id]
            self.upsert_task(task, parent_node)

    def upsert_task(self, task, parent_node):
        node = html.DIV(Class="task", Id=task.oid, draggable=True)
        _ = parent_node <= node
        self.draw_task(task)
        node.bind('dragstart', ev_callback(self.drag_start, task))
        node.bind('dragover', self.drag_over)
        node.bind('drop', ev_callback(self.drag_drop, task))
        node.bind('click', ev_callback(self.change_task_color, task, node))

    def draw_task(self, task):
        def do_tag(facet_, tag):
            sty = {"background-color": facet_.color, "font-size": "0.75rem", "text-align": "center"}
            f_div = html.SPAN(Class="box is-small is-rounded is-fullwidth mx-1 p-0", style=sty)
            # f_div = html.DIV(Class="tag is-rounded is-small", style={"background-color": facet_.color})
            # f_ico = html.I(Class=f"fa fa-{facet_.icon}")
            title = f"{facet_.name}:{tag.name}"
            if tag.icon.startswith("_"):
                t_ico = svg.svg()
                label = tag.icon[1:]
                img = svg.use(href=f"#{label}", x=0, y=0, width=11, height=11, transform=f"scale(0.16)")
                _ = t_ico <= img
            else:
                t_ico = html.I(Class=f"fa fa-{tag.icon}", style=dict(color=tag.color), title=title)
            # _ = f_div <= f_ico
            _ = f_div <= t_ico
            return html.TD(f_div, title=title, Class="td is-small")

        def do_icon(ico, data):
            _ico = html.TD(html.I(Class=f"fa fa-{ico}"), Class="dropdown")
            ico_ctn = html.DIV(Class="dropdown-content")
            # data = [":".join([dt[0], fi(dt[1]).strftime("%c")[4: -14]]) for dt in data] if ico == "calendar" else data
            _data = [":".join([dt[0], dt[1][5: -13]]) for dt in data] if ico == "calendar" else data
            _data = [":".join(dt) for dt in data] if ico == "tags" else _data
            _ = _ico <= ico_ctn
            spans = [html.DIV(html.SPAN(str(datum)) + html.BR()) for datum in _data if "_self" not in datum]
            if "links" in data:
                _ = [spn.bind("click", lambda *_: alert("not implemented")) for ix, spn in enumerate(spans) if ix != 1]
                spans[1].bind("click", lambda *_: TagView(task, self).draw())
            _ = [ico_ctn <= span for span in spans]
            return _ico if data else None

        node = doc[task.oid]
        node.html = ""
        node.style.backgroundColor = self.kanban.tasks_colors[task.color_id]
        facet = {key: IcoColor(key, *(value["_self"].split())) for key, value in _FACET.items()}
        facets = {fk: {tk: IcoColor(tk, *tv.split()) for tk, tv in fv.items() if tk != "_self"}
                  for fk, fv in _FACET.items()}
        # has to fix old version of facet that was code and now is 'develop'
        cmd = [do_tag(facet[_facet if _facet != "code" else "develop"],
                      facets[_facet if _facet != "code" else "develop"][_tag if _tag != "data" else "info"])
               for _facet, _tag in task.tags if _tag != "_self"]
        #  XXX - must remove these old versions - XXX
        # cmd = [do_tag(facet[_facet], _tag) for _facet, _tags in sample(list(facets.items()), randint(1, 6))
        #        for _tag in sample(list(_tags.values()), 1)]

        # progress = html.DIV(Class="task_progress")
        #
        # progress_text = html.P("%d%%" % task.progress,
        #                        Class="task_progress_text")
        # # _ = progress <= progress_text
        #
        # progress_bar = html.DIV(Class="task_progress_bar")
        # progress_bar.style.width = percent(task.progress)
        # _ = progress <= progress_bar XXX removed progress!
        icons = "external-link tags comment users calendar bars".split()
        menu = "links tags comment users progress calendar".split() + [task.oid]
        props = [task.external_links, task.tags, task.comments, task.users, task.calendar, menu]
        cmd += [do_icon(ico, data) for ico, data in zip(icons, props)]
        MenuView(task, self).draw(cmd[-1], node)
        # cmd[-1].bind("click", lambda *_: TagView(task, self).draw())
        # cmd += [html.TD(html.I(Class=f"fa fa-{ico}"), Class="task_command_delete") for ico in icons]

        # menu = html.I(Class="fa fa-bars")
        # command_delete = html.DIV(menu, Class="task_command_delete")
        icons = html.TR(Class="tr is-fullwidth")
        # html.TD(progress, Class="task_command") +
        #     cmd[0] + cmd[1] + cmd[2] + cmd[3] + cmd[4] + cmd[5] + cmd[7] + cmd[8] + cmd[2] + cmd[3] + cmd[4] + cmd[5]
        # )
        _ = [icons <= cm for cm in cmd if cm]
        # _ = node <= command
        desc = html.P(Id=f"desc {task.oid}", Class="task_desc")
        desc.html = task.desc
        _ = node <= html.TABLE(icons, Class="task_command")
        _ = node <= desc
        desc.bind('click', ev_callback(self.edit_task, task))
        self.draw_tasks(task, node)

        return
        #  +

        # html.TD(command_delete)), Class="task_command")

        #  XXX - must remove these old versions - XXX
        # progress.progress_bar = progress_bar
        # progress.progress_text = progress_text
        # progress.bind('click',
        #               ev_callback(self.make_task_progress, task, progress))

        # command_delete.bind('click', ev_callback(self.remove_task, task))

    def set_text(self, task):
        _ = self
        desc = doc[f"desc {task.oid}"]
        clear_node(desc)
        desc.html = task.desc

    def drag_start(self, ev, task):
        _ = self
        ev.data['text'] = task.oid
        ev.data.effectAllowed = 'move'

        ev.stopPropagation()

    def drag_over(self, ev):
        _ = self
        ev.preventDefault()

        ev.data.dropEffect = 'move'

    def drag_drop(self, ev, dst_task):
        ev.preventDefault()
        ev.stopPropagation()

        src_task_id = ev.data['text']
        src_task_node = doc[src_task_id]

        dst_task_id = dst_task.oid
        dst_task_node = doc[dst_task_id]

        _ = dst_task_node <= src_task_node
        task, orig_task, dst_task = self.kanban.move_task(src_task_id, dst_task_id)
        # [print(str(tsk)) for tsk in (task, orig_task, dst_task)]

        self.write(page=f"/api/item/{task.oid}", item=task)
        self.write(page=f"/api/item/{dst_task.oid}", item=dst_task)
        self.write(page=f"/api/item/{orig_task.oid}", item=orig_task)

    def add_task(self, ev, step, node):
        ev.stopPropagation()

        t = time.strftime(TIME_FMT)
        desc = prompt("New task", f"{step.desc} {t}")
        if desc:
            task = self.kanban.add_task(step.oid, desc, 0, 0)
            self.parse_desc(desc, task)
            self.upsert_task(task, node)
            self.write(page=f"/api/item/{task.oid}", item=task)

    def remove_task(self, ev, task):
        ev.stopPropagation()

        text = "Confirm deletion of: " + task.desc
        ret = confirm(text)
        if ret:
            del doc[task.oid]
            self.kanban.remove_task(task.oid)

    def change_task_color(self, ev, task, node):
        ev.stopPropagation()

        task.color_id = (task.color_id + 1) % len(self.kanban.tasks_colors)
        node.style.backgroundColor = self.kanban.tasks_colors[task.color_id]

    def make_task_progress(self, ev, task, node):
        _ = self
        ev.stopPropagation()

        task.progress = (task.progress + 25) % 125

        node.progress_bar.style.width = percent(task.progress)
        node.progress_text.text = percent(task.progress)

    def edit_task(self, ev, task):
        ev.stopPropagation()

        ret = prompt("Task", task.desc)
        if ret:
            task.desc = ret
            self.parse_desc(ret, task)
            self.set_text(task)
            self.draw_task(task)
            self.write(page=f"/api/item/{task.oid}", item=task)

    def load(self, *_):
        kanban = None
        if "kanban" in storage:
            txt = storage["kanban"]
            # noinspection PyBroadException
            try:
                eval("kanban = " + txt)
            except BaseException as _:
                kanban = None

            # noinspection PyBroadException
            try:
                if kanban is None:
                    raise KanbanException("could not load data from storage "
                                          "(use 'Save' to initialize it).")

                # noinspection PyUnresolvedReferences
                if kanban.schema_revision != self.kanban.schema_revision:
                    raise KanbanException("storage schema does not match "
                                          "application schema (use 'Save' to re-initialize it)")

                self.kanban = kanban

            except KanbanException as e:
                alert(e.msg)

            except:
                del storage["kanban"]

        self.draw()

    def save(self, *_):
        txt = instance_repr(self.kanban)
        storage["kanban"] = txt

    def dump(self, *_):
        # code = "storage['kanban'] = " + instance_repr(self.kanban)
        # code = json.dumps(self.kanban, default=json_repr)
        code = json.dumps(repr(self.kanban))
        alert(code)


class TagView:
    def __init__(self, task, view):
        self.dialog, self.section = None, None
        self.task, self.view = task, view
        self.do_modal = self.modal

    def modal(self):
        div, head, p, sect, foot, but = html.DIV, html.HEADER, html.P, html.SECTION, html.FOOTER, html.BUTTON
        head_title = p(f"Tags : {self.task.desc}", Class="title")
        header = head(head_title, Class="modal-card-head")
        self.section = section = sect(Class="modal-card-body")
        ok, cancel = but("OK", Class="button is-success"), but("Cancel", Class="button")
        ok.bind("click", self.edit)
        cancel.bind("click", lambda *_: self.dialog.classList.remove('is-active'))
        footer = foot(ok + cancel, Class="modal-card-foot")
        # _ = (div(Class ="modal")<= div(Class ="modal-background"))<= div(Class ="modal-card")
        self.dialog = div(div(div(header + section + footer, Class="modal-card"), Class="modal-background"),
                          Class="modal")
        _ = doc.body <= self.dialog
        self.do_modal = lambda *_: None
        print("did", self.dialog)

    def edit(self, *_):
        self.dialog.classList.remove('is-active')
        ...

    def draw(self):
        # self.do_modal()
        task = self.task
        # self.dialog.classList.add('is-active')
        facet = {fct[0]: fct[1] for fct in task.tags}

        dp = html.DIV(Class="panel")
        # _ = self.section <= dp
        db = html.DIV(Class="panel")
        # _ = self.section <= db

        def lb_for(tag, icon, color, title):
            return html.LABEL(
                html.I(Class=f"fa fa-{icon}", style=dict(color=color), title=title) + title[:4], For=tag)

        def rl(tag, icon, name):
            _tag = IcoColor(name, *(icon.split()))
            return (
                    (html.INPUT(type="radio", ID=tag, name=name, value=tag, checked="checked") if (
                            name in facet and tag == facet[name]) else html.INPUT(type="radio", ID=tag, name=name,
                                                                                  value=tag)) +
                    (lb_for(tag, _tag.icon, _tag.color, tag) if tag != "_self" else lb_for(tag, "ban", "magenta",
                                                                                           "none")))

        def fl(tag):
            return html.FIELDSET(ID=tag, Class="panel")

        ffs = {facet: IcoColor(facet, fl(tag=facet), tags["_self"].split()[1]) for facet, tags in _FACET.items()}

        def tag_div(child, _):
            # return html.DIV(child, Class="task_icon", style={"background-color": "slategray"})
            style = {"background-color": "slategray"}
            return html.DIV(child, Class="button is-small is-rounded is-fullwidth", style=style)

        _ = [[ffs[fs].icon <= tag_div(rl(tag, icon, fs), tags)
              for tag, icon in tags.items()] for fs, tags in _FACET.items()]
        rows = (dp, list(ffs.values())[:5]), (db, list(ffs.values())[5:])

        def facet_div(name, icon, color):
            cnt = html.DIV(html.DIV(html.DIV(icon, Class="media-content"), Class="media"), Class="card-content")
            return html.DIV(html.HEADER(html.P(name, Class="card-header-title"), Class="card-header") + cnt,
                            Class="card",
                            style=dict(display="inline-block", width="20%", backgroundColor=color))

        _ = [ad <= facet_div(_fs.name, _fs.icon, _fs.color)
             for ad, val in rows for _fs in val]
        # _ = [ad <= html.DIV(_fs.name + _fs.icon, Class="box m-0",
        #                     style=dict(display="inline-block", width="20%", backgroundColor=_fs.color))
        #      for ad, val in rows for _fs in val]
        # _ = [db <= html.DIV(_fs.name + _fs.icon, Class="box m-0",
        #                     style=dict(display="inline-block", width="20%", backgroundColor=_fs.color))
        #      for _fs in list(ffs.values())[5:]]
        return [dp, db]


class MenuView:
    def __init__(self, task, view):
        class Modal:
            def __init__(self):
                self.modal_div = self.section = self.footer = html.DIV()
                self.do_modal = self.modal
                self.tagging = html.DIV, html.HEADER, html.P, html.LABEL, html.INPUT, html.BUTTON, html.SPAN, html.I

            def modal(self):
                div, head, p, sect, foot, but = html.DIV, html.HEADER, html.P, html.SECTION, html.FOOTER, html.BUTTON
                head_title = p(f"Task : {here.task.desc}", Class="title")
                header = head(head_title, Class="modal-card-head")
                self.section = section = sect(Class="modal-card-body")
                ok, cancel = but("OK", Class="button is-success"), but("Cancel", Class="button")
                ok.bind("click", lambda *_: here.editor())
                cancel.bind("click", lambda *_: self.modal_div.classList.remove('is-active'))
                self.footer = footer = foot(ok + cancel, Class="modal-card-foot")
                # _ = (div(Class ="modal")<= div(Class ="modal-background"))<= div(Class ="modal-card")
                self.modal_div = div(div(div(header + section + footer, Class="modal-card"), Class="modal-background"),
                                     Class="modal")
                _ = doc.body <= self.modal_div
                self.do_modal = lambda *_: None
                # print("did", self.dialog)

            def form(self, temp, items):
                self.modal()
                contents = temp(items)
                # form = div(contents+inp(type="hidden", name="whatever", value="foobar"))
                _ = [self.section <= field for field in contents]
                self.modal_div.classList.add('is-active')

            def calendar(self, items):
                def edit(*_):
                    print("calendar edit")
                    [print(fld.value) for _, fld in fields]
                    self.modal_div.classList.remove('is-active')
                    ...

                div, head, p, lab, inp, but, sp, ic = self.tagging
                here.editor = edit
                # add = but("ADD", Class="button is-success")
                fields = [(eve, inp(Class="input", type="text", value=dater)) for eve, dater in items]
                return [div(div(lab(eve, Class="label") + input_field, Class="control"), Class="field")
                        for eve, input_field in fields]

            def tags(self, items):
                _ = self, items
                return here.tags.draw()

            def one_field(self, items, plc, ico):
                def adder(*_):
                    print("comment add")
                    _input = inp(Class="input", type="text", placeholder=plc)
                    fields.append(("", _input))
                    _ = self.section <= div(
                        div(_input + _icon, Class="control has-icons-left"), Class="field")

                def edit(*_):
                    print("comment edit")
                    [print(fld.value) for _, fld in fields]
                    self.modal_div.classList.remove('is-active')
                    ...

                div, head, p, lab, inp, but, sp, ic = self.tagging
                here.editor = edit
                add = but("ADD", Class="button is-primary")
                add.bind("click", adder)
                _icon = sp(ic(Class=ico), Class="icon is-small is-left")
                fields = [(eve, inp(Class="input", type="text", value=dater)) for eve, dater in items]
                return [div(div(input_field + _icon, Class="control has-icons-left"), Class="field")
                        for eve, input_field in fields] + [add]

            def comments(self, items):
                return self.one_field(items, "Add your comment here", "fa fa-comment")

            def users(self, items):
                return self.one_field(items, "Add a new partner here", "fa fa-users")

            def external_links(self, items):
                return self.one_field(items, "Add your link here", "fa fa-external-link")

        here = self
        self.editor = self.edit
        self.dialog = Modal()
        self.menu = None
        self.task, self.view = task, view
        self.tags = TagView(task, view)

    def edit(self, *_):
        self.dialog.modal_div.classList.remove('is-active')

    def draw(self, dropper, node):
        dlg = self.dialog
        _ic = "fa fa-{}"
        # _ico = html.SPAN(html.I(Class=), Class="icon")
        icons = "external-link tags comment users calendar battery-empty palette".split()
        mark = "links tags comment users calendar progress color".split()
        batt_colors = "gray red orange green blue".split()
        batt = [(cl, ico, tt) for cl, ico, tt in zip(batt_colors, BATT, '0% 25% 50% 75% 100%'.split())]
        colors = [(cl, ico, tt) for cl, ico, tt in zip(TASKS_COLORS, ["palette"] * 30, [""] * 30)]
        dialogs = dlg.external_links, dlg.tags, dlg.comments, dlg.users, dlg.calendar, batt, colors
        tsk = self.task
        arguments = tsk.external_links, tsk.tags, tsk.comments, tsk.users, tsk.calendar, tsk.progress, tsk.color_id
        menu_items = list(zip(mark, icons, arguments, dialogs))

        def popups(nam, ic, it, dl):
            def pop_editor(ev, iid):
                ev.stopPropagation()
                ev.preventDefault()
                self.task.color_id = iid if ic == "palette" else None
                node.style.backgroundColor = self.view.kanban.tasks_colors[iid] if ic == "palette" else None
                print("pop_editor", iid, activ)

            def menu_item(color, icon, title, iid=0):
                tit = color if ic == "palette" else title
                _ico = html.I(Class=f"fa fa-{icon}", style=dict(color=color), title=tit)
                # return html.A(html.SPAN(html.SPAN(_ico, Class="icon") + title, Class="icon-text"))
                _item_class = "icon-text is-activ" if iid == it else "icon-text"
                _item = html.LI(html.SPAN(_ico, Class="icon") + html.SPAN(title), Class=_item_class)
                _item.bind("click", lambda ev: pop_editor(ev, iid))
                return _item

            ico_ctn = html.LI()
            _ = [ico_ctn <= menu_item(iid=iid, *_dialogs) for iid, _dialogs in enumerate(dl[:20])]
            na = html.SPAN(nam)
            activ = it  # [-2] if len(dl) < 5 else it[-1]
            an = html.DIV(html.SPAN(html.SPAN(html.I(Class=f"fa fa-{ic}"), Class="icon") + na, Class="icon-text"))
            item_ = html.LI(an + html.UL(ico_ctn))
            # _ = an <= ico_ctn
            # an.bind("click", lambda *_: self.dialog.form(dl, it))
            # items = [html.LI(html.A(name)+sub_item(name, it, dl)) for name, it, dl in menu_items]
            return item_

        def item(nam, ic, it, dl):
            def item_editor(ev):
                ev.stopPropagation()
                ev.preventDefault()
                self.dialog.form(dl, it)
            na = html.SPAN(nam)
            an = html.SPAN(html.SPAN(html.I(Class=f"fa fa-{ic}"), Class="icon") + na, Class="icon-text")

            item_ = html.LI(an)

            an.bind("click", lambda ev: item_editor(ev))
            # items = [html.LI(html.A(name)+sub_item(name, it, dl)) for name, it, dl in menu_items]
            return item_

        items = [item(*its) for its in menu_items[:-2]] + [popups(*its) for its in menu_items[-2:]]
        menu = html.UL()
        _ = [menu <= it for it in items]
        self.menu = html.ASIDE(menu, Class="menu")
        _ = dropper <= html.DIV(self.menu, Class="dropdown-content")


# ----------------------------------------------------------
def clear_node(node):
    node.clear()


# ----------------------------------------------------------
def percent(p):
    return ("%d" % p) + "%"


# ----------------------------------------------------------
def instance_repr(o):
    if isinstance(o, dict):
        items = []
        for key, value in o.items():
            repr_key = instance_repr(key)
            repr_value = instance_repr(value)
            items.append(f"{repr_key} : {repr_value}")
        s = "{{ {} }}".format("\n, ".join(items))

    elif isinstance(o, list):
        items = [instance_repr(i) for i in o]
        s = "[ {} ]".format("\n, ".join(items))

    elif isinstance(o, set):
        items = [instance_repr(i) for i in o]
        s = "{{ {} }}".format("\n, ".join(items))

    elif isinstance(o, float):
        s = str(o)

    elif isinstance(o, int):
        s = str(o)

    elif isinstance(o, str):
        s = quoted_escape_string(o)

    else:
        attributes = dir(o)
        items = []
        for n in attributes:
            if not n.startswith("__"):
                repr_key = escape_string(n)
                repr_value = instance_repr(getattr(o, n))
                items.append(f"{repr_key} = {repr_value}")
        s = "{}( {} )".format(o.__class__.__name__, ", ".join(items))

    return s


# ----------------------------------------------------------
def json_repr(o):
    if isinstance(o, dict):
        return {k: repr(v) for k, v in o.items()}
    if isinstance(o, tuple) or isinstance(o, list) or isinstance(o, set):
        # return [repr(i) for i in o]
        return [i for i in o]

    elif isinstance(o, float) or isinstance(o, int):
        return str(o)

    elif isinstance(o, str):
        return o
        # return quoted_escape_string(o)

    else:
        attributes = [
            n for n in o.__dict__ if not n.startswith("__") and not callable(n) and not type(n) is staticmethod]
        # print(o.__class__.__name__, attributes)
        return {k: json_repr(getattr(o, k)) for k in attributes if getattr(o, k)}
        # return {o.__class__.__name__: {k: json_repr(getattr(o, k)) for k in attributes if getattr(o, k)}}
        # for n in attributes:
        #     if not n.startswith("__") and not callable(n) and not type(n) is staticmethod:
        #         repr_key = escape_string(n)
        #         repr_value = repr(getattr(o, n))
        #         items.append(f"{repr_key} = {repr_value}")
        # return "{}( {} )".format(o.__class__.__name__, ", ".join(items))


# ----------------------------------------------------------
def quoted_escape_string(s):
    s = "'{}'".format(escape_string(s))
    return s


# ----------------------------------------------------------
def escape_string(s):
    # TODO other control characters
    s = s.replace("'", "\\'")
    return s


# ----------------------------------------------------------
def ev_callback(method, *args):
    def cb(ev):
        return method(ev, *args)

    return cb


# ----------------------------------------------------------
def init_demo(kanban):
    def init_model():
        from random import sample, randint, choice
        for tsk_id, tsk_obj in kanban.tasks.items():
            tags = [(fc, choice(list(tg.keys()))) for fc, tg in sample(list(_FACET.items()), randint(1, 3))
                    if tsk_id.startswith("task")]
            tsk_obj.tags = tags

    for color_id, desc in enumerate(STEPS):
        kanban.add_step(desc, color_id)

    kanban.add_task("step1", 'Project A<br>Add new Feature <b>A3</b>', 0, 0)
    kanban.add_task("step1", 'Project B<br>Add new Feature <b>B2</b>', 0, 0)

    task = kanban.add_task("step2", 'Project B<br>Feature <b>B1</b>', 3, 50)
    kanban.add_task(task.oid, 'Check B1.1 with XXX', 4, 75)
    kanban.add_task(task.oid, 'Wait for YYY to clarify B1.2', 4, 25)
    kanban.add_task(task.oid, 'Started B1.3', 2, 25)

    task = kanban.add_task("step3", 'A1', 3, 75)
    kanban.add_task(task.oid, 'Dynamic design', 2, 75)
    kanban.add_task(task.oid, 'Static design', 1, 100)

    kanban.add_task("step4", 'A2 Coding', 0, 0)

    task = kanban.add_task("step5", 'Project C', 3, 0)
    kanban.add_task(task.oid, 'Waiting QA', 4, 0)

    kanban.add_task("step6", 'Project D', 1, 100)
    init_model()


def main():
    kanban = KanbanModel(counter=1, schema_revision=SCHEMA_REVISION,
                         steps_colors=STEPS_COLORS, tasks_colors=TASKS_COLORS)

    _copyright = """
        Copyright (c) 2013-2014, Pedro Rodriguez pedro.rodriguez.web@gmail.com
        All rights reserved.
        Redistribution and use in source and binary forms, with or without modification,
        are permitted provided that the following conditions are met:

        Redistributions of source code must retain the above copyright notice,
        this list of conditions and the following disclaimer.
        Redistributions in binary form must reproduce the above copyright notice,
        this list of conditions and the following disclaimer in the documentation
        and/or other materials provided with the distribution.
        Neither the name of the <ORGANIZATION> nor the names of its contributors
        may be used to endorse or promote products derived from this software without specific prior written permission.

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
        AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
        THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
        IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
        DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
        (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
        OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
        WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
        ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    """
    ret = True  # confirm("Click OK to accept condition of use\n\n" + _copyright)

    if ret:
        # init_demo(kanban)
        kanban_view = KanbanView(kanban)
        # kanban_view.write(0)
        kanban_view.read()
        # kanban_view.load()
    else:
        doc.open("about:blank")


# ----------------------------------------------------------
if __name__ == '__main__':
    main()
