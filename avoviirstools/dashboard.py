#!/usr/bin/env python

# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import zmq
from datetime import datetime
import threading
from dash.dependencies import Input, Output
from posttroll.message import Message
import os
import os.path
import numpy as np
import pandas as pd
import time

UPDATE_PUBLISHER = "tcp://viirscollector:19191"
SDR_PUBLISHER = "tcp://viirscollector:29092"
PICKLE_DIR = "/viirs/pickle"
UPDATE_PICKLE = os.path.join(PICKLE_DIR, "task_queue.pickle")
SDR_PICKLE = os.path.join(PICKLE_DIR, "sdr.pickle")
PICKLING_INTERAL = 5 * 60

waiting_tasks_lock = threading.Lock()
datafiles_lock = threading.Lock()

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    children=[
        # header
        html.Div(
            [html.Span("VIIRS Processing", className="app-title")],
            className="row header",
        ),
        html.Div(
            children="""
        AVO VIIRS status
    """
        ),
        dcc.Graph(id="products-waiting", className="six columns"),
        dcc.Interval(id="products-waiting-update", interval=1000, n_intervals=0),
        dcc.Graph(id="datafile-latency", className="six columns row"),
        dcc.Interval(id="datafile-latency-update", interval=5000, n_intervals=0),
    ]
)


@app.callback(
    Output("products-waiting", "figure"),
    [Input("products-waiting-update", "n_intervals")],
)
def gen_products_waiting(interval):
    figure = {
        "data": [
            {
                "x": waiting_tasks.index,
                "y": waiting_tasks["count"],
                "type": "scatter",
                "name": "Products Waiting",
                "hovertext": waiting_tasks["products"],
            }
        ],
        "layout": {
            "title": "VIIRS Products waiting to be generated",
            "xaxis": {"type": "date", "rangemode": "nonnegative"},
            "yaxis": {"rangemode": "nonnegative"},
        },
    }

    return figure


@app.callback(
    Output("datafile-latency", "figure"),
    [Input("datafile-latency-update", "n_intervals")],
)
def gen_datafile_latency(interval):
    figure = {
        "data": [
            {
                "x": datafiles.index,
                "y": datafiles,
                "type": "scatter",
                "name": "Datafile Latency",
            }
        ],
        "layout": {
            "title": "AVO Data File Latency",
            "xaxis": {"type": "date", "rangemode": "nonnegative"},
        },
    }

    return figure


class SdrSubscriber(threading.Thread):
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "pytroll://AVO/viirs/sdr")
        self.socket.connect(SDR_PUBLISHER)

    def run(self):
        print("starting SDR subscriber loop")
        while True:
            msg_bytes = self.socket.recv()
            print("GOT SDR: {}".format(msg_bytes))
            npnow = np.datetime64("now")
            message = Message.decode(msg_bytes)
            filename = os.path.basename(message.data["uri"])
            file_time = datetime.strptime(filename[-69:-51], "_d%Y%m%d_t%H%M%S")
            npthen = np.datetime64(file_time)
            latency = (npnow - npthen) / np.timedelta64(1, "s")
            datafiles[npnow] = latency


class UpdateSubscriber(threading.Thread):
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.socket.connect(UPDATE_PUBLISHER)

    def run(self):
        while True:
            message = self.socket.recv_json()
            queue_length = message["queue length"]
            products = ":".join(message["products waiting"])
            npnow = np.datetime64("now")
            with waiting_tasks_lock:
                waiting_tasks.at[npnow] = (queue_length, products)


class UpdateFlusher(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("constructing flisher")

    def run(self):
        while True:
            print("starting updateflusher loop")
            time.sleep(PICKLING_INTERAL)
            print("flushing")
            yesterday = np.datetime64("now") - np.timedelta64(1, "D")
            with waiting_tasks_lock:
                waiting_tasks.truncate(before=yesterday)
                copy = waiting_tasks.copy(deep=True)

            copy.to_pickle(os.path.join(UPDATE_PICKLE))

            last_week = np.datetime64("now") - np.timedelta64(1, "W")
            with datafiles_lock:
                datafiles.truncate(before=last_week)
                copy = datafiles.copy(deep=True)

            copy.to_pickle(os.path.join(SDR_PICKLE))


def initialize():
    global waiting_tasks
    if os.path.exists(UPDATE_PICKLE):
        print("loading {}".format(UPDATE_PICKLE))
        waiting_tasks = pd.read_pickle(UPDATE_PICKLE)
    else:
        waiting_tasks = pd.DataFrame(columns=["count", "products"])
        print("Can't find {}".format(UPDATE_PICKLE))

    global datafiles
    if os.path.exists(SDR_PICKLE):
        print("loading {}".format(SDR_PICKLE))
        datafiles = pd.read_pickle(SDR_PICKLE)
    else:
        datafiles = pd.Series()
        print("Can't find {}".format(SDR_PICKLE))


def main():
    context = zmq.Context()

    initialize()
    update_subscriber = UpdateSubscriber(context)
    update_subscriber.start()

    update_flusher = UpdateFlusher()
    update_flusher.start()

    sdr_subscriber = SdrSubscriber(context)
    sdr_subscriber.start()

    app.run_server(host="0.0.0.0")


if __name__ == "__main__":
    main()
