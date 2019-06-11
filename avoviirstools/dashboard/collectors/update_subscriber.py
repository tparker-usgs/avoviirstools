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
            self._waiting_tasks = pd.read_pickle(UPDATE_PICKLE)
            self._test_queue = self._waiting_tasks.index.to_list()
        else:
            print("Can't find {}".format(UPDATE_PICKLE))
            self._waiting_tasks = pd.Series()
            self._test_queue = []

    @property
    def waiting_tasks(self):
        print(
            "TOMP SAYS1: {} :: {} :: {} :: {} :: {} :: {}".format(
                pd.to_datetime("now"),
                self._waiting_tasks.size,
                id(self),
                id(self._waiting_tasks),
                id(self._waiting_tasks.index),
                len(self._test_queue),
            )
        )
        return self._waiting_tasks.copy()

    def flush(self):
        print("Flushing UpdateSubscriber")
        new_start = pd.to_datetime("now") - pd.Timedelta("14 days")
        with self.lock:
            self._waiting_tasks = self._waiting_tasks.truncate(before=new_start)
            self._waiting_tasks = self._waiting_tasks.resample("1min").apply("max")
            copy = self._waiting_tasks.copy()

        copy.to_pickle(os.path.join(UPDATE_PICKLE))

    def run(self):
        print("Starting update subscriber")
        while True:
            test = self.waiting_tasks
            message = self.socket.recv_json()
            npnow = pd.to_datetime("now")
            with self.lock:
                self._waiting_tasks[npnow] = message["queue length"]
                self._test_queue.append(npnow)
