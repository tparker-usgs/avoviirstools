from .sdr_subscriber import SdrSubscriber
from .app import zmq_context, app


sdr_subscriber = SdrSubscriber(zmq_context)
        #self.data = self.sdr_subscriber.sdrs.copy()

class DataArrival:
    def __init__(self):
        sdr_subscriber.start()

    def flush(self):
        sdr_subscriber.flush()


@app.callback(
    Output("last-seen-table", "data"),
    [Input("last-seen-table-update", "n_clicks")],
)
def gen_last_seen_table(n_clicks):
    npp_data = sdr_subscriber.sdrs.loc[data["platform_name"] == "Suomi-NPP"]
    j01_data = sdr_subscriber.sdrs.loc[data["platform_name"] == "NOAA-20"]

    if npp_data.size > 0:
        npp_gap = "{} minutes ago".format(npp_data["gap"].iloc[-1])
    else:
        npp_gap = "never"

    if j01_data.size > 0:
        j01_gap = "{} minutes ago".format(j01_data["gap"].iloc[-1])
    else:
        j01_gap = "never"

    return [
            {"platform": "Suomi-NPP", "last seen": npp_gap},
            {"platform": "NOAA-20", "last seen": j01_gap},
        ]

