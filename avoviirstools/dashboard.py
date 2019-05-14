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
import numpy as np
import time


UPDATE_PUBLISHER = "tcp://viirscollector:19191"
SDR_PUBLISHER = "tcp://viirscollector:29092"
waiting_tasks = np.empty(259200, dtype=[('time', '>i4'), ('count', '>i2')])
datafiles = np.empty(259200, dtype=[('time', '>i4'), ('latency', '>i2')])


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


@app.callback(Output('products-waiting', 'figure'),
              [Input('products-waiting-update', 'n_intervals')])
def gen_wind_speed(interval):
    figure={
        'data': [
            {'x': waiting_tasks['time'], 'y': waiting_tasks['count'],
             'type': 'scatter', 'name': 'Products Waiting'},
        ],
        'layout': {
            'title': 'VIIRS Products waiting to be generated'
        }
    }

    return figure


@app.callback(Output('datafile-latency', 'figure'),
              [Input('datafile-latency-update', 'n_intervals')])
def gen_datafile_latency(interval):
    figure={
        'data': [
            {'x': datafiles['time'], 'y': datafiles['latency'],
             'type': 'scatter', 'name': 'Datafile Latency'},
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
        self.index = 0

    def run(self):
        while True:
            msg_bytes = self.socket.recv()
            now = time.time()
            message = Message.decode(msg_bytes)
            filename = os.path.basename(message.data['uri'])
            file_time = datetime.strptime(filename[-69:-51],
                                          "_d%Y%m%d_t%H%M%S")
            datafiles[self.index] = (now, now - file_time)
            self.index = (self.index + 1) % len(datafiles)


class UpdateSubscriber(threading.Thread):
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')
        self.socket.connect(UPDATE_PUBLISHER)
        self.index = 0

    def run(self):
        while True:
            queue_length = self.socket.recv_json()['queue length']
            waiting_tasks[self.index] = (time.time(), queue_length)
            self.index = (self.index + 1) % len(waiting_tasks)


def main():
    context = zmq.Context()
    update_subscriber = UpdateSubscriber(context)
    update_subscriber.start()

    app.run_server(debug=True, host="0.0.0.0")


if __name__ == '__main__':
    main()