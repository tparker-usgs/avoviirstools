import zmq
import threading
import os
import os.path
import pandas as pd


UPDATE_PUBLISHER = "tcp://viirscollector:19191"
PICKLE_DIR = "/viirs/pickle"
UPDATE_PICKLE = os.path.join(PICKLE_DIR, "task_queue.pickle")


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
        print("Flushing UpdateSubscriber")
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
