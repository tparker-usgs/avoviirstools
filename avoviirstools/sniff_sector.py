#!/usr/bin/env python

# -*- coding: utf-8 -*-

# I waive copyright and related rights in the this work worldwide
# through the CC0 1.0 Universal public domain dedication.
# https://creativecommons.org/publicdomain/zero/1.0/legalcode

# Author(s):
#   Tom Parker <tparker@usgs.gov>

""" watch sdr retrieved sdr files
"""

import zmq
import signal
import time

SECTOR_PUBLISHER = "tcp://viirstools:29392"


def main():
    # let ctrl-c work as it should.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
    socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 60)
    socket.setsockopt(zmq.TCP_KEEPALIVE_CNT, 20)
    socket.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 60)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    socket.connect(SECTOR_PUBLISHER)

    while True:
        msg = socket.recv_json()
        time_str = time.strftime("%x %X", time.gmtime())
        print("{} | {}".format(time_str, msg))


if __name__ == "__main__":
    main()
