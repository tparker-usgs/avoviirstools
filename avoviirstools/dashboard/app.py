#!/usr/bin/env python

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


PICKLING_INTERAL = 5 * 60

context = zmq.Context()
update_subscriber = UpdateSubscriber(context)
sdr_subscriber = SdrSubscriber(context)

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/milligram/1.3.0/milligram.css"]
app = dash.Dash(__name__, external_stylesheets=external_css)
app.layout = html.Div(
    [
        html.Div([html.H1("AVO VIIRS Processing")]),
        html.Div(
            [
                html.Div([html.H3("Products Waiting")], className="row"),
                dcc.Checklist(
                    id="products-waiting-auto",
                    options=[{"label": "Auto Update", "value": "Auto"}],
                    values=[],
                    className="row",
                ),
                html.Div(
                    [
                        dcc.Graph(id="products-waiting", className=""),
                        dcc.Interval(
                            id="products-waiting-update", interval=1000, n_intervals=0
                        ),
                    ],
                    className="row",
                ),
            ]
        ),
        html.Div(
            [
                html.Div([html.H3("SDR Delivery Time")], className="row"),
                dcc.Checklist(
                    id="datafile-latency-auto",
                    options=[{"label": "Auto Update", "value": "Auto"}],
                    values=[],
                    className="row",
                ),
                html.Div(
                    [
                        dcc.Graph(id="datafile-latency"),
                        dcc.Interval(
                            id="datafile-latency-update", interval=5000, n_intervals=0
                        ),
                    ],
                    className="row",
                ),
            ]
        ),
        html.Div(
            [
                dcc.Checklist(
                    id="sdr-table-auto",
                    options=[{"label": "Auto Update", "value": "Auto"}],
                    values=[],
                    className="row",
                ),
                html.Div(
                    [
                        dash_table.DataTable(id="sdr-table"),
                        dcc.Interval(
                            id="sdr-table-update", interval=5000, n_intervals=0
                        ),
                    ],
                    className="row",
                ),
            ]
        ),
    ],
    className="container",
)


@app.callback(Output("sdr-table", "data"), [Input("sdr-table-update", "n_intervals")])
def update_sdr_table(interval):
    return sdr_subscriber.sdrs.to_dict('records')


@app.callback(
    Output("sdr-table", "columns"), [Input("sdr-table-update", "n_intervals")]
)
def update_sdr_table_cols(interval):
    return [
        {"name": i, "id": i, "deletable": True}
        for i in sdr_subscriber.sdrs.columns.to_list()
    ]


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
    sdrs = sdr_subscriber.sdrs
    figure = {
        "data": [
            {
                "x": sdrs.index,
                "y": sdrs["delay"],
                "type": "scatter",
                "name": "Datafile Latency",
                "fill": "tozeroy",
            }
        ],
        "layout": {
            "title": "AVO Data File Latency",
            "xaxis": {"type": "date", "rangemode": "nonnegative"},
        },
    }

    return figure


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
