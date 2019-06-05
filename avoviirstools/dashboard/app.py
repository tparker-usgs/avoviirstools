#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
import dash
import threading
import time
import flask
import dash_html_components as html

from .layout.volcview_images import volcview_images_layout

from .layout.product_generation import product_generation_layout

from .layout.data_arrival import data_arrival_layout


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


def gen_layout():
    return html.Div(
        [
            html.Div(
                [html.H1("AVO VIIRS Processing", style={"fontFamily": "Merriweather"})],
                className="row justify-content-center",
            ),
            volcview_images_layout(),
            product_generation_layout(),
            data_arrival_layout(),
        ],
        className="container-fluid",
    )


flusher = Flusher()
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_css)
app.layout = gen_layout()
init_callbacks(flusher)
flusher.start()
