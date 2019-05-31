from dash.dependencies import Input, Output
from .sector_subscriber import SectorSubscriber
from .app import zmq_context, app

sector_subscriber = SectorSubscriber(zmq_context)


class VolcviewImages:
    def __init__(self):
        sector_subscriber.start()

    def flush(self):
        sector_subscriber.flush()


@app.callback(
    Output("volcview-sectors", "figure"), [Input("volcview-sectors-update", "n_clicks")]
)
def gen_datafile_gap(n_clicks):
    data = sector_subscriber.sector_images.groupby("sector").size()

    return {
        "data": {"x": data.index, "y": data, "type": "bar", "name": "num images"},
        "layout": {
            "xaxis": {"type": "date", "rangemode": "nonnegative"},
            "yaxis": {"title": "Interfile Gap (min)", "range": [0, 500]},
        },
    }
