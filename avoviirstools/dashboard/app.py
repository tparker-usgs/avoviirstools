#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
import dash
import zmq
import threading
import time

PICKLING_INTERVAL = 5 * 60
external_css = [
    "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
]
zmq_context = zmq.Context()
app = dash.Dash(__name__, external_stylesheets=external_css)


class Flusher(threading.Thread):
    def __init__(self, *args):
        threading.Thread.__init__(self)
        self.flushables = list(args)

    def run(self):
        while True:
            time.sleep(PICKLING_INTERVAL)
            print("flushing")
            for flushable in self.flushables:
                flushable.flush()


def main():
    flusher = Flusher()

    from avoviirstools.dashboard.layout import apply_layout

    apply_layout()

    from avoviirstools.dashboard.data_arrival import DataArrival

    data_arrival = DataArrival()
    flusher.flushables.append(data_arrival)

    from avoviirstools.dashboard.product_generation import ProductGeneration

    product_generation = ProductGeneration()
    flusher.flushables.append(product_generation)

    from avoviirstools.dashboard.volcview_images import VolcviewImages

    volcview_images = VolcviewImages()
    flusher.flushables.append(volcview_images)

    flusher.start()

    app.run_server(host="0.0.0.0")


if __name__ == "__main__":
    main()
