#!/usr/bin/env python

# -*- coding: utf-8 -*-

# I waive copyright and related rights in the this work worldwide
# through the CC0 1.0 Universal public domain dedication.
# https://creativecommons.org/publicdomain/zero/1.0/legalcode

# Author(s):
#   Tom Parker <tparker@usgs.gov>

""" proxy sector image messages
"""
import zmq


def main():
    context = zmq.Context()
    frontend = context.socket(zmq.SUB)
    frontend.setsockopt(zmq.SUBSCRIBE, "")
    frontend.bind("tcp://*:29292")

    backend = context.socket(zmq.PUB)
    backend.bind("tcp://*:29392")

    zmq.proxy(frontend, backend)


if __name__ == "__main__":
    main()
