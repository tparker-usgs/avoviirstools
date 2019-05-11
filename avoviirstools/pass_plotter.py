#!/usr/bin/env python


import argparse
from posttroll.message import Message
from avoviirsprocessor.coreprocessors import * # NOQA
import threading
import zmq
import tomputils.util as tutil
import collections
from datetime import timedelta
import time


DATA_PUBLISHER = "tcp://viirscollector:29092"
logger = tutil.setup_logging("pass_plotter errors")
ORBIT_SLACK = timedelta(minutes=30)
message_q_lock = threading.Lock()


def _arg_parse():
    description = "Reprocesses a serialized message in a file."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("message", help="path to serialized message")

    return parser.parse_args()


class DataSubscriber(threading.Thread):
    def __init__(self, context, message_q):
        threading.Thread.__init__(self)
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, 'pytroll://AVO/viirs/sdr')
        self.socket.connect(DATA_PUBLISHER)
        self.message_q = message_q

    def run(self):
        while True:
            msg_bytes = self.socket.recv()
            message = Message.decode(msg_bytes)
            self.message_q.append(message)


def main():

    message_q = collections.OrderedDict()
    context = zmq.Context()
    updater = DataSubscriber(context, message_q)
    updater.start()
    logger.info("updater started")

    while True:
        for message in message_q:
            with message_q_lock:
                message = message_q.pop()
            print(message)
        time.sleep(1)


if __name__ == '__main__':
    main()
