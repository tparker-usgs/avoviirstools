from dash.dependencies import Input, Output
from .sdr_subscriber import SdrSubscriber
from .app import zmq_context, app
import pandas as pd

sdr_subscriber = SdrSubscriber(zmq_context)


class DataArrival:
    def __init__(self):
        sdr_subscriber.start()

    def flush(self):
        sdr_subscriber.flush()


@app.callback(
    Output("last-seen-table", "data"), [Input("last-seen-table-update", "n_clicks")]
)
def gen_last_seen_table(n_clicks):
    data = []
    for platform in ["Suomi-NPP", "NOAA-20"]:
        platform_data = sdr_subscriber.sdrs.loc[
            sdr_subscriber.sdrs["platform_name"] == "Suomi-NPP"
        ]
        if platform_data.size > 0:
            last_seen = "{} minutes ago".format(
                platform_data["gap"].iloc[-1] / pd.Timedelta("60 seconds")
            )
        else:
            last_seen = "Never"
        data.append({"platform": platform, "last seen": last_seen})

    return data


@app.callback(
    Output("datafile-latency", "figure"), [Input("datafile-latency-update", "n_clicks")]
)
def gen_datafile_latency(n_clicks):
    npp_data = sdr_subscriber.sdrs.loc[
        sdr_subscriber.sdrs["platform_name"] == "Suomi-NPP"
    ]
    j01_data = sdr_subscriber.sdrs.loc[
        sdr_subscriber.sdrs["platform_name"] == "NOAA-20"
    ]

    return {
        "data": [
            {
                "x": npp_data.index,
                "y": npp_data["delay"].astype("timedelta64[m]"),
                "type": "scatter",
                "name": "Suomi-NPP",
            },
            {
                "x": j01_data.index,
                "y": j01_data["delay"].astype("timedelta64[m]"),
                "type": "scatter",
                "name": "NOAA-20",
            },
        ],
        "layout": {
            "xaxis": {"type": "date"},
            "yaxis": {"title": "SDR Latency minutes"},
        },
    }


@app.callback(
    Output("datafile-gap", "figure"), [Input("datafile-gap-update", "n_clicks")]
)
def gen_datafile_gap(n_clicks):
    npp_data = sdr_subscriber.sdrs.loc[
        sdr_subscriber.sdrs["platform_name"] == "Suomi-NPP"
    ]
    j01_data = sdr_subscriber.sdrs.loc[
        sdr_subscriber.sdrs["platform_name"] == "NOAA-20"
    ]

    return {
        "data": [
            {
                "x": npp_data.index,
                "y": npp_data["gap"],
                "type": "scatter",
                "name": "Suomi-NPP",
            },
            {
                "x": j01_data.index,
                "y": j01_data["gap"],
                "type": "scatter",
                "name": "NOAA-20",
            },
        ],
        "layout": {
            "xaxis": {"type": "date", "rangemode": "nonnegative"},
            "yaxis": {"title": "Interfile Gap", "range": [0, 200]},
        },
    }


@app.callback(
    Output("sdr-table", "data"),
    [Input("sdr-table", "pagination_settings"), Input("sdr-table-platform", "value")],
)
def gen_sdr_table(pagination_settings, value):
    data = sdr_subscriber.sdrs
    data = data.iloc[
        pagination_settings["current_page"]
        * pagination_settings["page_size"] : (pagination_settings["current_page"] + 1)
        * pagination_settings["page_size"]
    ]
    data = data.loc[sdr_subscriber.sdrs["platform_name"] == value]

    return data.to_dict("records")[-2::-1]
