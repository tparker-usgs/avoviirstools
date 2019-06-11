#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
import dash
import threading
import time
import flask
import zmq

from .collectors.update_subscriber import UpdateSubscriber
from .collectors.sdr_subscriber import SdrSubscriber
from .collectors.sector_subscriber import SectorSubscriber

PICKLING_INTERVAL = 5 * 60

# external_scripts = [
#     {
#         "src": "https://code.jquery.com/jquery-3.2.1.slim.min.js",
#         "integrity": "sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN",  # NOQA: E501
#         "crossorigin": "anonymous",
#     },
#     {
#         "src": "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js",  # NOQA: E501
#         "integrity": "sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q",  # NOQA: E501
#         "crossorigin": "anonymous",
#     },
#     {
#         "src": "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js",  # NOQA: E501
#         "integrity": "sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl",  # NOQA: E501
#         "crossorigin": "anonymous",
#     },
#     "/assets/enable_popover.js",
# ]

external_css = [
    "https://fonts.googleapis.com/css?family=Merriweather:300&display=swap",
    "https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
    {
        "href": "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css",  # NOQA: E501
        "rel": "stylesheet",
        "integrity": "sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T",  # NOQA: E501
        "crossorigin": "anonymous",
    },
    "/assets/style.css",
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


def gen_layout():
    from .layout import gen_layout

    return gen_layout()


flusher = Flusher()
zmq_context = zmq.Context()

update_subscriber = UpdateSubscriber(zmq_context)
update_subscriber.start()
flusher.flushables.append(update_subscriber)

sdr_subscriber = SdrSubscriber(zmq_context)
sdr_subscriber.start()
flusher.flushables.append(sdr_subscriber)

sector_subscriber = SectorSubscriber(zmq_context)
sector_subscriber.start()
flusher.flushables.append(sector_subscriber)

server = flask.Flask(__name__)
app = dash.Dash(
    __name__,
    server=server,
    # external_scripts=external_scripts,
    external_stylesheets=external_css,
)
app.layout = gen_layout()
from . import callbacks  # NOQA: F401

flusher.start()
