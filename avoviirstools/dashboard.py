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
import numpy as np


UPDATE_PUBLISHER = "tcp://viirscollector:19191"
SDR_PUBLISHER = "tcp://viirscollector:29092"

waiting_tasks = np.empty(
    60 * 60 * 24, dtype=[("time", "datetime64[s]"), ("count", "i4"), ("products", "U")]
)
waiting_tasks["time"][:] = np.datetime64("NaT")

datafiles = np.empty(1500, dtype=[("time", "datetime64[s]"), ("latency", "i4")])
datafiles["time"][:] = np.datetime64("NaT")

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    children=[
        html.H1(children="VIIRS Processesing"),
        html.Div(
            children="""
        AVO VIIRS status
    """
        ),
        dcc.Graph(id="products-waiting"),
        dcc.Interval(id="products-waiting-update", interval=1000, n_intervals=0),
        dcc.Graph(id="datafile-latency"),
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
                "x": waiting_tasks["time"],
                "y": waiting_tasks["count"],
                "type": "scatter",
                "name": "Products Waiting",
                "hoverinfo": waiting_tasks["products"],
            }
        ],
        "layout": {
            "title": "VIIRS Products waiting to be generated",
            "xaxis": {"type": "date", "rangemode": "nonnegative"},
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
                "x": datafiles["time"],
                "y": datafiles["latency"],
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
        index = 0
        print("starting SDR subscriber loop")
        while True:
            msg_bytes = self.socket.recv()
            npnow = np.datetime64("now")
            message = Message.decode(msg_bytes)
            filename = os.path.basename(message.data["uri"])
            file_time = datetime.strptime(filename[-69:-51], "_d%Y%m%d_t%H%M%S")
            npthen = np.datetime64(file_time)
            latency = (npnow - npthen) / np.timedelta64(1, "s")
            datafiles[index] = (npnow, latency)
            print("{}: {} @ {}".format(index.npnow, npthen))
            index = (index + 1) % len(datafiles)


class UpdateSubscriber(threading.Thread):
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.socket.connect(UPDATE_PUBLISHER)

    def run(self):
        index = 0
        while True:
            message = self.socket.recv_json()
            queue_length = message["queue length"]
            products = ":".join(message["products waiting"])
            npnow = np.datetime64("now")
            waiting_tasks[index] = (npnow, queue_length, products)

            index = (index + 1) % len(waiting_tasks)


def main():
    context = zmq.Context()

    update_subscriber = UpdateSubscriber(context)
    update_subscriber.start()

    sdr_subscriber = SdrSubscriber(context)
    sdr_subscriber.start()

    app.run_server(host="0.0.0.0")


if __name__ == "__main__":
    main()
