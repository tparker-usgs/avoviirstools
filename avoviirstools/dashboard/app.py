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


def last_seen_table(npp_data, j01_data):
    if npp_data.size > 0:
        npp_gap = "{} minutes ago".format(npp_data["gap"].iloc[-1])
    else:
        npp_gap = "never"

    if j01_data.size > 0:
        j01_gap = "{} minutes ago".format(j01_data["gap"].iloc[-1])
    else:
        j01_gap = "never"

    return dash_table.DataTable(
        id="last-seen-table",
        columns=[
            {"name": "", "id": "platform"},
            {"name": "Last Seen", "id": "last seen"},
        ],
        data=[
            {"platform": "Suomi-NPP", "last seen": npp_gap},
            {"platform": "NOAA-20", "last seen": j01_gap},
        ],
        style_as_list_view=True,
        style_table={"width": "300px", "margin": "0px auto"},
    )


def datafile_latency(npp_data, j01_data):
    return dcc.Graph(
        id="datafile-latency",
        style={"height": "300px"},
        figure={
            "data": [
                {
                    "x": npp_data.index,
                    "y": npp_data["delay"],
                    "type": "scatter",
                    "name": "Suomi-NPP",
                },
                {
                    "x": j01_data.index,
                    "y": j01_data["delay"],
                    "type": "scatter",
                    "name": "NOAA-20",
                },
            ],
            "layout": {
                "xaxis": {"type": "date"},
                "yaxis": {"title": "SDR Latency minutes"},
            },
        },
    )


def datafile_gap(npp_data, j01_data):
    return dcc.Graph(
        id="datafile-gap",
        style={"height": "300px"},
        figure={
            "data": [
                {
                    "x": npp_data.index,
                    "y": npp_data["gap"],
                    "type": "scatter",
                    "name": "Suomi-NPP",
                },
                {
                    "x": j01_data.index,
                    "y": j01_data["gap"],
                    "type": "scatter",
                    "name": "NOAA-20",
                },
            ],
            "layout": {
                "xaxis": {"type": "date", "rangemode": "nonnegative"},
                "yaxis": {"title": "Interfile Gap", "range": [0, 200]},
            },
        },
    )


def datafile_table(npp_data, j01_data):
    columns = [
        {"name": "orbit", "id": "orbit_number"},
        {"name": "segment", "id": "segment"},
        {"name": "data start", "id": "start_time_str"},
        {"name": "aquisition time", "id": "aquisition time"},
        {"name": "AVO aquisition delay (min)", "id": "delay"},
        {"name": "data age (min)", "id": "age"},
    ]

    tooltips = {
        "aquisition time": "When did the data arrive at AVO?",
        "delay": "How long did it take for the data to arrive at AVO?",
        "age": "How old is the data?",
    }

    return dash_table.DataTable(
        id="sdr-table",
        data=j01_data.to_dict("records")[-2::-1],
        columns=columns,
        column_static_tooltip=tooltips,
        pagination_settings={"current_page": 0, "page_size": 5},
        pagination_mode="fe",
        style_table={"maxHeight": "300px"},
        style_as_list_view=True,
        style_header={"minWidth": "0px", "maxWidth": "250px", "whiteSpace": "normal"},
        style_cell={"padding": "10px"},
        css=[
            {
                "selector": ".dash-cell div.dash-cell-value",
                "rule": "display: inline; white-space: inherit;"
                " overflow: inherit; text-overflow: inherit;",
            }
        ],
    )


def sdrs():
    data = sdr_subscriber.sdrs.copy()
    data["age"] = pd.to_datetime("now") - data["start_time"]
    data["age"] = data["age"].fillna(pd.Timedelta("0 seconds"))
    data["age"] = data["age"] / pd.Timedelta("60 seconds")
    data["age"] = data["age"].astype("int64")
    data["aquisition time"] = data.index.to_series().dt.strftime("%m/%d/%Y %H:%M")

    npp_data = data.loc[data["platform_name"] == "Suomi-NPP"]
    j01_data = data.loc[data["platform_name"] == "NOAA-20"]

    return html.Div(
        [
            html.Div(
                [
                    last_seen_table(npp_data, j01_data),
                    datafile_latency(npp_data, j01_data),
                    datafile_gap(npp_data, j01_data),
                ],
                className="col-5",
            ),
            html.Div([datafile_table(npp_data, j01_data)], className="col-7"),
        ],
        className="row justify-content-center",
    )


external_css = [
    "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
]
app = dash.Dash(__name__, external_stylesheets=external_css)
app.layout = html.Div(
    [
        html.Div(
            [html.H1("AVO VIIRS Processing")], className="row justify-content-center"
        ),
        html.Div([html.H3("Product Generation")], className="row"),
        products_waiting(),
        html.Div([html.H3("Data Arrival")], className="row"),
        sdrs(),
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
