#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
import dash
import threading
import time
import flask

PICKLING_INTERVAL = 5 * 60
external_css = [
    "https://fonts.googleapis.com/css?family=Merriweather:300&display=swap",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css",
    "https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
]


class Flusher(threading.Thread):
    def __init__(self, *args):
        threading.Thread.__init__(self)
        self.flushables = list(args)

    def run(self):
        while True:
            time.sleep(PICKLING_INTERVAL)
            print("flushing")
            for flushable in self.flushables:
                flushable.flush()


def init_callbacks(flusher):
    from .callbacks import init_callbacks

    init_callbacks(flusher)


def gen_layout(flusher):
    from .layout import gen_layout

    return gen_layout(flusher)


flusher = Flusher()
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_css)
app.layout = gen_layout()
init_callbacks(flusher)
flusher.start()
