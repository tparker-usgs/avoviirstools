# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#  Purpose: Tools for maintaining IIRS processing at AVO
#   Author: Tom Parker
#
# -----------------------------------------------------------------------------
"""
avoviirstools
=========

Tools for maintaining IIRS processing at AVO

:license:
    CC0 1.0 Universal
    http://creativecommons.org/publicdomain/zero/1.0/
"""


from avoviirstools.version import __version__
import zmq

zmq_context = zmq.Context()

__all__ = ["__version__", "zmq_context"]
