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


PICKLING_INTERAL = 5 * 60

context = zmq.Context()
update_subscriber = UpdateSubscriber(context)
sdr_subscriber = SdrSubscriber(context)


def products_waiting():
    return html.Div(
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
                    dcc.Graph(id="products-waiting"),
                    dcc.Interval(
                        id="products-waiting-update", interval=5000, n_intervals=0
                    ),
                ],
                className="row",
            ),
        ],
        className="container",
    )


def sdrs(platform):
    sdrs = sdr_subscriber.sdrs
    columns = ["segment", "start_time", "orbit_number", "delay"]
    data = sdrs.loc[sdrs["platform_name"] == platform][columns].to_dict("records")

    columns = [ {"name": i, "id": i} for i in columns ]
    return html.Div(
        [
            html.Div(
                [html.H3("{} SDR".format(platform))], className="row"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(
                                id="datafile-latency-{}".format(platform),
                                style={"height": "300px"},
                                figure={
                                    "data": [
                                        {
                                            "x": sdrs.index,
                                            "y": sdrs.loc[
                                                sdrs["platform_name"] == platform
                                            ]["delay"]
                                            / 60,
                                            "type": "scatter",
                                            "name": "Datafile Latency",
                                            "fill": "tozeroy",
                                        }
                                    ],
                                    "layout": {
                                        "xaxis": {
                                            "type": "date",
                                            "rangemode": "nonnegative",
                                        },
                                        "yaxis": {"title": "SDR Latency minutes"},
                                    },
                                },
                            )
                        ],
                        className="column column-25",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    dash_table.DataTable(
                                        id="sdr-table-{}".format(platform),
                                        data=data,
                                        columns=columns,
                                        pagination_settings={
                                            "current_page": 0,
                                            "page_size": 8,
                                        },
                                        pagination_mode="fe",
                                        style_table={
                                            "maxHeight": "300px",
                                        },
                                    )
                                ]
                            )
                        ],
                        className="column column-75",
                    ),
                ],
                className="row",
            ),
        ],
        className="container",
    )


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/milligram/1.3.0/milligram.css"]
app = dash.Dash(__name__, external_stylesheets=external_css)
app.layout = html.Div(
    [
        html.Div([html.H1("AVO VIIRS Processing")], className="row"),
        products_waiting(),
        sdrs("Suomi-NPP"),
        sdrs("NOAA-20"),
    ]
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
            "title": "VIIRS Products waiting to be generated",
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
