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
                    dcc.Graph(id="products-waiting"),
                    dcc.Interval(
                        id="products-waiting-update", interval=5000, n_intervals=0
                    ),
                ],
                className="col",
            ),
        ],
        className="row align-items-center",
    )


def sdrs(platform):
    pdnow = pd.to_datetime("now")
    sdrs = sdr_subscriber.sdrs
    columns = ["segment", "start_time", "orbit_number", "delay"]
    data = sdrs.loc[sdrs["platform_name"] == platform][columns]

    data["gap"] = data.index.to_series().diff()
    data["gap"] = data["gap"].fillna(pd.Timedelta("0 seconds"))
    data.at[pdnow, "gap"] = pdnow - data.index[-1]
    data["gap"] = data["gap"] / pd.Timedelta("60 seconds")
    data["gap"] = data["gap"].astype("int64")

    data["age"] = pd.to_datetime("now") - data["start_time"]
    data["age"] = data["age"].fillna(pd.Timedelta("0 seconds"))
    data["age"] = data["age"] / pd.Timedelta("60 seconds")
    data["age"] = data["age"].astype("int64")

    data["start_time"] = data["start_time"].dt.strftime("%m/%d/%Y %H:%M")

    data["delay"] = data["delay"] / 60
    data["delay"] = data["delay"].fillna(0)
    data["delay"] = data["delay"].astype("int64")

    data["aquisition time"] = data.index.strftime("%m/%d/%Y %H:%M")

    columns = [
        {"name": "orbit", "id": "orbit_number"},
        {"name": "segment", "id": "segment"},
        {"name": "data start", "id": "start_time"},
        {"name": "aquisition time", "id": "aquisition time"},
        {"name": "AVO aquisition delay (min)", "id": "delay"},
        {"name": "data age (min)", "id": "age"},
    ]

    tooltips = {
        "aquisition time": "When did the data arrive at AVO?",
        "delay": "How long did it take for the data to arrive at AVO?",
        "age": "How old is the data?",
    }

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    dash_table.DataTable(
                                        id="last-sdr-table".format(platform),
                                        data=[{"name": "Suomi-NPP", "last seen": npp_data.at[pdnow, "gap"]}, {"name": "NOAA-20", "last seen": j01_data.at[pdnow, "gap"]}],
                                        columns=[{name="", id="name"},{name="Last Seen", id="last seend"}],
                                        style_as_list_view=True,
                                    )
                                ]
                            ), className="row",),
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
                                            "y": data["delay"],
                                            "type": "scatter",
                                            "name": "Datafile Latency",
                                            "fill": "tozeroy",
                                        },
                                        {
                                            "x": sdrs.index,
                                            "y": data["gap"],
                                            "type": "scatter",
                                            "name": "Datafile Gap",
                                        },
                                    ],
                                    "layout": {
                                        "xaxis": {
                                            "type": "date",
                                            "rangemode": "nonnegative",
                                        },
                                        "yaxis": {
                                            "title": "SDR Latency minutes",
                                            "range": [0, 200],
                                        },
                                    },
                                },
                            )
                        ],
                        className="col",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    dash_table.DataTable(
                                        id="sdr-table-{}".format(platform),
                                        data=data.to_dict("records")[-2::-1],
                                        columns=columns,
                                        column_static_tooltip=tooltips,
                                        pagination_settings={
                                            "current_page": 0,
                                            "page_size": 5,
                                        },
                                        pagination_mode="fe",
                                        style_table={"maxHeight": "300px"},
                                        style_as_list_view=True,
                                        style_header={
                                            "minWidth": "0px",
                                            "maxWidth": "250px",
                                            "whiteSpace": "normal",
                                        },
                                        style_cell={"padding": "10px"},
                                        css=[
                                            {
                                                "selector": ".dash-cell div.dash-cell-value",
                                                "rule": "display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;",
                                            }
                                        ],
                                    )
                                ]
                            )
                        ],
                        className="col",
                    ),
                ],
                className="row",
            ),
            ]
        )

external_css = [
    "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
]
app = dash.Dash(__name__, external_stylesheets=external_css)
app.layout = html.Div(
    [
        html.Div([html.H1("AVO VIIRS Processing")], className="row justify-content-center"),
        html.Div([html.H3("Product Generation")], className="row"),
        products_waiting(),
        html.Div([html.H3("Data Arrival")], className="row"),
        sdrs("Suomi-NPP"),
        sdrs("NOAA-20"),
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
