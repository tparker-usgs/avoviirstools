from dash.dependencies import Input, Output
from .sector_subscriber import SectorSubscriber
from .app import zmq_context, app

sector_subscriber = SectorSubscriber(zmq_context)


class VolcviewImages:
    def __init__(self):
        sector_subscriber.start()

    def flush(self):
        sector_subscriber.flush()
