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
from posttroll.message import Message
import signal

SDR_PUBLISHER = "tcp://viirscollector:29092"


def main():
    # let ctrl-c work as it should.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, 'pytroll://AVO/viirs/sdr')
    socket.connect(SDR_PUBLISHER)

    while True:
        msg_bytes = socket.recv()
        message = Message.decode(msg_bytes)
        print(message)

if __name__ == '__main__':
    main()
