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
import os.path
import time
from datetime import datetime
import humanize


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
        filename = os.path.basename(message.data['uri'])
        file_time = datetime.strptime(filename[-69:-51], "_d%Y%m%d_t%H%M%S")
        age = datetime.now() - file_time
        print("{} (retrieval took {})".format(filename, humanize.naturaldelta(age)))

if __name__ == '__main__':
    main()
