#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import zmq
import threading
from dash.dependencies import Input, Output
import time
from avoviirstools.dashboard.updaters import UpdateSubscriber, SdrSubscriber
import pandas as pd
import avoviirstools.dashboard.data_arrival


PICKLING_INTERAL = 5 * 60

context = zmq.Context()
update_subscriber = UpdateSubscriber(context)
sdr_subscriber = SdrSubscriber(context)


def products_waiting():
    return html.Div(
        [
            dcc.Checklist(
                id="products-waiting-auto",
                options=[{"label": "Auto Update", "value": "Auto"}],
                values=["Auto"],
                className="col-auto",
            ),
            html.Div(
                [
                    dcc.Graph(id="products-waiting", style={"height": "350px"}),
                    dcc.Interval(
                        id="products-waiting-update", interval=5000, n_intervals=0
                    ),
                ],
                className="col",
            ),
        ],
        className="row align-items-center",
    )


external_css = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_css)
app.layout = html.Div(
    [
        html.Div(
            [html.H1("AVO VIIRS Processing")],
            className="row justify-content-center bg-primary",
        ),
        html.Div([html.H3("Volcview Sectors")], className="row bg-secondary"),
        html.Div([html.H3("Product Generation")], className="row bg-secondary"),
        products_waiting(),
        html.Div([html.H3("Data Arrival")], className="row bg-secondary"),
        avoviirstools.dashboard.data_arrival.sdrs(),
    ],
    className="container-fluid",
)


@app.callback(
    Output("products-waiting", "figure"),
    [Input("products-waiting-update", "n_intervals")],
)
def gen_products_waiting(interval):
    waiting_tasks = update_subscriber.updates
    figure = {
        "data": [
            {
                "x": waiting_tasks.index,
                "y": waiting_tasks,
                "type": "scatter",
                "name": "Products Waiting",
                "fill": "tozeroy",
            }
        ],
        "layout": {
            "xaxis": {"type": "date", "rangemode": "nonnegative"},
            "title": "Products waiting to be generated",
        },
    }

    return figure


@app.callback(
    Output("products-waiting-update", "disabled"),
    [Input("products-waiting-auto", "values")],
)
def update_refresh(auto_values):
    return "Auto" not in auto_values


class Flusher(threading.Thread):
    def __init__(self, *args):
        threading.Thread.__init__(self)
        self.flushables = list(args)

    def run(self):
        while True:
            time.sleep(PICKLING_INTERAL)
            print("flushing")
            for flushable in self.flushables:
                flushable.flush()


def main():
    flusher = Flusher()
    flusher.start()

    update_subscriber.start()
    flusher.flushables.append(update_subscriber)

    sdr_subscriber.start()
    flusher.flushables.append(sdr_subscriber)

    app.run_server(host="0.0.0.0")


if __name__ == "__main__":
    main()
