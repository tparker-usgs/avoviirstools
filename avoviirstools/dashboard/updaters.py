#!/usr/bin/env python

# -*- coding: utf-8 -*-
import zmq
from datetime import datetime
import threading
from posttroll.message import Message
import os
import os.path
import pandas as pd


UPDATE_PUBLISHER = "tcp://viirscollector:19191"
SDR_PUBLISHER = "tcp://viirscollector:29092"
PICKLE_DIR = "/viirs/pickle"
UPDATE_PICKLE = os.path.join(PICKLE_DIR, "task_queue.pickle")
SDR_PICKLE = os.path.join(PICKLE_DIR, "sdr2.pickle")


class SdrSubscriber(threading.Thread):
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "pytroll://AVO/viirs/sdr")
        self.socket.connect(SDR_PUBLISHER)
        self.lock = threading.Lock()
        self.initalize()

    def initalize(self):
        if os.path.exists(SDR_PICKLE):
            print("loading {}".format(SDR_PICKLE))
            self._sdrs = pd.read_pickle(SDR_PICKLE)
        else:
            print("Can't find {}".format(SDR_PICKLE))
            self.datafiles = pd.Series()
            self._sdrs = pd.DataFrame(
                columns=[
                    "segment",
                    "platform_name",
                    "start_time",
                    "end_time",
                    "orbit_number",
                    "proctime",
                    "uid",
                    "delay",
                ]
            )
            self._sdrs = self._sdrs.astype(
                dtype={
                    "segment": "object",
                    "platform_name": "object",
                    "start_time": "datetime64[s]",
                    "end_time": "datetime64[s]",
                    "orbit_number": "int64",
                    "proctime": "datetime64[s]",
                    "uid": "int64",
                    "delay": "timedelta64[s]",
                }
            )
            self._sdrs.index = self._sdrs.index.to_series().astype("datetime64[s]")

        self._sdrs["gap"] = self._sdrs.index.to_series().diff()
        self._sdrs["start_time_str"] = self._sdrs["start_time"].dt.strftime(
            "%m/%d/%Y %H:%M"
        )
        self._sdrs = self._sdrs.astype(
            dtype={"gap": "timedelta64[s]", "start_time_str": "object"}
        )

    @property
    def sdrs(self):
        return self._sdrs

    def flush(self):
        last_week = pd.to_datetime("now") - pd.Timedelta("7 days")
        with self.lock:
            self._sdrs.truncate(before=last_week)
            columns = [
                "segment",
                "platform_name",
                "start_time",
                "end_time",
                "orbit_number",
                "proctime",
                "uid",
                "delay",
            ]
            copy = self._sdrs[columns].copy(deep=True)

        copy.to_pickle(os.path.join(SDR_PICKLE))

    def run(self):
        print("starting SDR subscriber loop")
        while True:
            msg_bytes = self.socket.recv()
            print("GOT SDR: {}".format(msg_bytes))
            npnow = pd.to_datetime("now")
            message = Message.decode(msg_bytes)
            filename = os.path.basename(message.data["uri"])
            file_time = datetime.strptime(filename[-69:-51], "_d%Y%m%d_t%H%M%S")
            npthen = pd.to_datetime(file_time)
            delay = (npnow - npthen) / pd.Timedelta("1 s")
            sdrs = self.sdrs
            if sdrs.index.size > 0:
                gap = npnow - sdrs.index[-1]
            else:
                gap = -1

            with self.lock:
                print("TOMP SAYS: {}".format(sdrs))
                print("TOMP SAYS: {}".format(sdrs.columns))
                self._sdrs.at[npnow] = (
                    message.data["segment"],
                    message.data["platform_name"],
                    pd.to_datetime(message.data["start_time"]),
                    pd.to_datetime(message.data["end_time"]),
                    message.data["orbit_number"],
                    pd.to_datetime(message.data["proctime"]),
                    message.data["uid"],
                    delay,
                    gap,
                    message.data["start_time"].strftime("%m/%d/%Y %H:%M"),
                )


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
            print("Can't find {}".format(UPDATE_PICKLE))
            self.waiting_tasks = pd.Series()

    @property
    def updates(self):
        return self.waiting_tasks

    def flush(self):
        lastweek = pd.to_datetime("now") - pd.Timedelta("7 days")
        with self.lock:
            self.waiting_tasks.truncate(before=lastweek)
            self.waiting_tasks = self.waiting_tasks.resample("1min").apply("max")
            copy = self.waiting_tasks.copy()

        copy.to_pickle(os.path.join(UPDATE_PICKLE))

    def run(self):
        while True:
            message = self.socket.recv_json()
            npnow = pd.to_datetime("now")
            with self.lock:
                self.waiting_tasks[npnow] = message["queue length"]
