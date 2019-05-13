#!/usr/bin/env python

# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import zmq
from datetime import datetime
import collections
import threading
from dash.dependencies import Input, Output
from posttroll.message import Message
import os

UPDATE_PUBLISHER = "tcp://viirscollector:19191"
SDR_PUBLISHER = "tcp://viirscollector:29092"

#waiting_tasks_times = collections.deque(maxlen=259200)
#waiting_tasks_counts = collections.deque(maxlen=259200)
waiting_tasks_times = []
waiting_tasks_counts = []
datafile_times = []
datafile_latencies = []

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='VIIRS Processesing'),

    html.Div(children='''
        AVO VIIRS status
    '''),

    dcc.Graph(id='products-waiting'),
    dcc.Interval(id='products-waiting-update', interval=1000, n_intervals=0),
    dcc.Graph(id='datafile-latency'),
    dcc.Interval(id='datafile-latency-update', interval=5000, n_intervals=0),
])


@app.callback(Output('products-waiting', 'figure'), [Input('products-waiting-update', 'n_intervals')])
def gen_wind_speed(interval):
    figure={
        'data': [
            {'x': waiting_tasks_times, 'y': waiting_tasks_counts, 'type': 'scatter', 'name': 'Products Waiting'},
        ],
        'layout': {
            'title': 'VIIRS Products waiting to be generated'
        }
    }

    return figure


@app.callback(Output('datafile-latency', 'figure'), [Input('datafile-latency-update', 'n_intervals')])
def gen_datafile_latency(interval):
    figure={
        'data': [
            {'x': datafile_times, 'y': datafile_latencies, 'type': 'scatter', 'name': 'Datafile Latency'},
        ],
        'layout': {
            'title': 'AVO Data File Latency'
        }
    }

    return figure


class SdrSubscriber(threading.Thread):
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, 'pytroll://AVO/viirs/sdr')
        self.socket.connect(SDR_PUBLISHER)

    def run(self):
        while True:
            msg_bytes = self.socket.recv()
            now = datetime.now()
            datafile_times.append(now)
            message = Message.decode(msg_bytes)
            filename = os.path.basename(message.data['uri'])
            file_time = datetime.strptime(filename[-69:-51],
                                          "_d%Y%m%d_t%H%M%S")
            datafile_latencies.append(now - file_time)


class UpdateSubscriber(threading.Thread):
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')
        self.socket.connect(UPDATE_PUBLISHER)

    def run(self):
        while True:
            waiting_tasks_counts.append(self.socket.recv_json()['queue length'])
            waiting_tasks_times.append(datetime.now())


def main():
    context = zmq.Context()
    update_subscriber = UpdateSubscriber(context)
    update_subscriber.start()

    app.run_server(debug=True, host="0.0.0.0")


if __name__ == '__main__':
    main()