import zmq
import threading
import os
import os.path
import pandas as pd


SECTOR_PUBLISHER = "tcp://viirstools:29392"
PICKLE_DIR = "/viirs/pickle"
SECTOR_PICKLE = os.path.join(PICKLE_DIR, "sector.pickle")


class SectorSubscriber(threading.Thread):
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.socket.connect(SECTOR_PUBLISHER)
        self.lock = threading.Lock()
        self.initialize()

    def initialize(self):
        if os.path.exists(SECTOR_PICKLE):
            print("loading {}".format(SECTOR_PICKLE))
            self._sector_images = pd.read_pickle(SECTOR_PICKLE)
        else:
            print("Can't find {}".format(SECTOR_PICKLE))
            self._sector_images = pd.DataFrame(
                columns=["sector", "band", "dataType", "imageUnixtime"]
            )
            self._sector_images = self._sector_images.astype(
                dtype={"imageUnixtime": "int64"}
            )
            self._sector_images.index = self._sector_images.index.to_series().astype(
                "datetime64[s]"
            )

    @property
    def sector_images(self):
        return self._sector_images

    def flush(self):
        print("Flushing SectorSubscriber")
        new_start = pd.to_datetime("now") - pd.Timedelta("14 days")
        with self.lock:
            self._sector_images = self._sector_images.truncate(before=new_start)
            copy = self._sector_images.copy()

        copy.to_pickle(os.path.join(SECTOR_PICKLE))

    def run(self):
        while True:
            message = self.socket.recv_json()
            npnow = pd.to_datetime("now")
            with self.lock:
                self._sector_images.at[npnow] = (
                    message["sector"],
                    message["band"],
                    message["dataType"],
                    message["imageUnixtime"],
                )
            print("TOMP SAYS SECTOR: {}".format(message))
