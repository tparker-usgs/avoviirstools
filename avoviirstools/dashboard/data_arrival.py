from .sdr_subscriber import SdrSubscriber
from .app import zmq_context


class DataArrival:
    def __init__(self):
        self.sdr_subscriber = SdrSubscriber(zmq_context)
        self.sdr_subscriber.start()
        self.data = self.sdr_subscriber.sdrs.copy()

    def flush(self):
        self.sdr_subscriber.flush()
