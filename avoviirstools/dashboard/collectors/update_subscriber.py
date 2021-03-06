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
        self.socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
        self.socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 60)
        self.socket.setsockopt(zmq.TCP_KEEPALIVE_CNT, 20)
        self.socket.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 60)
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

    @property
    def waiting_tasks(self):
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
            message = self.socket.recv_json()
            npnow = pd.to_datetime("now")
            with self.lock:
                self._waiting_tasks[npnow] = message["queue length"]
