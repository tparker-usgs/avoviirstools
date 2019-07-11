#!/usr/bin/env python

# -*- coding: utf-8 -*-

# I waive copyright and related rights in the this work worldwide
# through the CC0 1.0 Universal public domain dedication.
# https://creativecommons.org/publicdomain/zero/1.0/legalcode

# Author(s):
#   Tom Parker <tparker@usgs.gov>

""" display task_broker updates
"""

import argparse
import zmq
import signal
import time

UPDATE_PUBLISHER = "tcp://viirscollector:19191"


def _arg_parse():
    description = "Displays messages from the product queue, "
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-l", "--length", help="Print current queue length", action="store_true"
    )
    return parser.parse_args()


def sniff_queue(socket):
    while True:
        msg = socket.recv_json()
        time_str = time.strftime("%x %X", time.gmtime())
        print("{} | {}".format(time_str, msg))


def print_length(socket):
    print(socket.recv_json()["queue length"])


def main():
    # let ctrl-c work as it should.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    args = _arg_parse()
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
    socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 60)
    socket.setsockopt(zmq.TCP_KEEPALIVE_CNT, 20)
    socket.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 60)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    socket.connect(UPDATE_PUBLISHER)

    if args.length:
        print_length(socket)
    else:
        sniff_queue(socket)


if __name__ == "__main__":
    main()
