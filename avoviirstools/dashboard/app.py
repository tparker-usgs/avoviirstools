#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
import dash
import dash_html_components as html
import zmq
import threading
import time
from avoviirstools.dashboard.data_arrival import DataArrival
from avoviirstools.dashboard.product_generation import ProductGeneration

PICKLING_INTERVAL = 5 * 60
external_css = [
    "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
]
zmq_context = zmq.Context()
app = dash.Dash(__name__, external_stylesheets=external_css)


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


def apply_layout(app):
    app.layout = html.Div(
        [
            html.Div(
                [html.H1("AVO VIIRS Processing")],
                className="row justify-content-center bg-primary",
            ),
            html.Div([html.H3("Volcview Sectors")], className="row bg-secondary"),
            html.Div([html.H3("Product Generation")], className="row bg-secondary"),
            avoviirstools.dashboard.product_generation.products_waiting(),
            html.Div([html.H3("Data Arrival")], className="row bg-secondary"),
            avoviirstools.dashboard.data_arrival.data_arrival_pane(),
        ],
        className="container-fluid",
    )


def main():
    flusher = Flusher()

    data_arrival = DataArrival(zmq_context, app)
    flusher.flushables.append(data_arrival)

    product_generation = ProductGeneration(zmq_context, app)
    flusher.flushables.append(product_generation)

    apply_layout(app, data_arrival, product_generation)
    flusher.start()

    app.run_server(host="0.0.0.0")


if __name__ == "__main__":
    main()
