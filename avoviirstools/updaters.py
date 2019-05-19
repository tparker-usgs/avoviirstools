#!/usr/bin/env python

# -*- coding: utf-8 -*-
import zmq
from datetime import datetime
import threading
from posttroll.message import Message
import os
import os.path
import numpy as np
import pandas as pd


UPDATE_PUBLISHER = "tcp://viirscollector:19191"
SDR_PUBLISHER = "tcp://viirscollector:29092"
PICKLE_DIR = "/viirs/pickle"
UPDATE_PICKLE = os.path.join(PICKLE_DIR, "task_queue.pickle")
SDR_PICKLE = os.path.join(PICKLE_DIR, "sdr.pickle")


class SdrSubscriber(threading.Thread):
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "pytroll://AVO/viirs/sdr")
        self.socket.connect(SDR_PUBLISHER)
        self.lock = threading.Lock()

    def initalize(self):
        if os.path.exists(SDR_PICKLE):
            print("loading {}".format(SDR_PICKLE))
            self.datafiles = pd.read_pickle(SDR_PICKLE)
        else:
            print("Can't find {}".format(SDR_PICKLE))
            self.datafiles = pd.Series()

    @property
    def sdrs(self):
        return self.datafiles

    def flush(self):
        last_week = np.datetime64("now") - np.timedelta64(1, "W")
        with self.lock:
            self.datafiles.truncate(before=last_week)
            copy = self.datafiles.copy(deep=True)

        copy.to_pickle(os.path.join(SDR_PICKLE))

    def run(self):
        print("starting SDR subscriber loop")
        while True:
            msg_bytes = self.socket.recv()
            print("GOT SDR: {}".format(msg_bytes))
            npnow = np.datetime64("now")
            message = Message.decode(msg_bytes)
            filename = os.path.basename(message.data["uri"])
            file_time = datetime.strptime(filename[-69:-51], "_d%Y%m%d_t%H%M%S")
            npthen = np.datetime64(file_time)
            latency = (npnow - npthen) / np.timedelta64(1, "s")
            with self.lock:
                self.datafiles[npnow] = latency


class UpdateSubscriber(threading.Thread):
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.socket.connect(UPDATE_PUBLISHER)
        self.lock = threading.Lock()
        self.initialize()

    def initialize(self):
        if os.path.exists(UPDATE_PICKLE):
            print("loading {}".format(UPDATE_PICKLE))
            self.waiting_tasks = pd.read_pickle(UPDATE_PICKLE)
        else:
            self.waiting_tasks = pd.DataFrame(columns=["count", "products"])
            print("Can't find {}".format(UPDATE_PICKLE))

    @property
    def updates(self):
        return self.waiting_tasks

    def flush(self):
        lastweek = np.datetime64("now") - np.timedelta64(7, "D")
        with self.lock:
            self.waiting_tasks.truncate(before=lastweek)
            self.waiting_tasks = self.waiting_tasks.resample("1min").apply(
                {"count": "max", "waiting products": "update"}
            )
            copy = self.waiting_tasks.copy(deep=True)

        copy.to_pickle(os.path.join(UPDATE_PICKLE))

    def run(self):
        while True:
            message = self.socket.recv_json()
            queue_length = message["queue length"]
            products = set(message["products waiting"])
            npnow = np.datetime64("now")
            with self.lock:
                self.waiting_tasks.at[npnow] = (queue_length, products)
