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
        html.Div([html.Div([html.H3("SDRs")], className="row")]),
        html.Div(
            [
                html.Div(
                    [
                        dash_table.DataTable(
                            id="sdr-table",
                            data=sdr_subscriber.sdrs.to_dict(),
                            columns=[
                                {"name": i, "id": i}
                                for i in sdr_subscriber.sdrs.columns.to_list()
                            ],
                        )
                    ],
                    className="row",
                )
            ]
        ),
    ],
    className="container",
)


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

    print("TOMP SAYS: {}".format(sdr_subscriber.sdrs.to_dict()))
    update_subscriber.start()
    flusher.flushables.append(update_subscriber)

    sdr_subscriber.start()
    flusher.flushables.append(sdr_subscriber)

    app.run_server(host="0.0.0.0")


if __name__ == "__main__":
    main()
