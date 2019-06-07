from dash.dependencies import Input, Output
import pandas as pd

from .. import app

YELLOW_THREASHOLD = 0.9
RED_THREASHOLD = 0.5


@app.callback(
    Output("last-seen-table", "data"), [Input("last-seen-table-update", "n_clicks")]
)
def gen_last_seen_table(n_clicks):
    data = []
    for platform in ["Suomi-NPP", "NOAA-20"]:
        platform_data = app.sdr_subscriber.sdrs.loc[
            app.sdr_subscriber.sdrs["platform_name"] == platform
        ]
        if platform_data.size > 0:
            pdnow = pd.to_datetime("now")
            last_seen = pdnow - platform_data.index.max()
            last_seen = last_seen / pd.Timedelta("60 seconds")
            last_seen = "{:.0f} minutes ago".format(last_seen)
        else:
            last_seen = "Never"
        data.append({"platform": platform, "last seen": last_seen})

    return data


@app.callback(
    Output("datafile-latency", "figure"), [Input("datafile-latency-update", "n_clicks")]
)
def gen_datafile_latency(n_clicks):
    data = []
    for platform in ["Suomi-NPP", "NOAA-20"]:
        platform_data = app.sdr_subscriber.sdrs.loc[
            app.sdr_subscriber.sdrs["platform_name"] == platform
        ]

        data.append(
            {
                "x": platform_data.index,
                "y": platform_data["delay"].astype("timedelta64[m]"),
                "type": "scatter",
                "name": platform,
            }
        )

    return {"data": data, "layout": {"xaxis": {"type": "date"}}}


@app.callback(
    Output("datafile-gap", "figure"), [Input("datafile-gap-update", "n_clicks")]
)
def gen_datafile_gap(n_clicks):
    data = []
    for platform in ["Suomi-NPP", "NOAA-20"]:
        platform_data = app.sdr_subscriber.sdrs.loc[
            app.sdr_subscriber.sdrs["platform_name"] == platform
        ]

        data.append(
            {
                "x": platform_data.index,
                "y": platform_data["gap"] / pd.Timedelta("60 seconds"),
                "type": "scatter",
                "name": platform,
            }
        )

    return {
        "data": data,
        "layout": {"xaxis": {"type": "date", "rangemode": "nonnegative"}},
    }


@app.callback(
    Output("sdr-table", "data"),
    [Input("sdr-table", "pagination_settings"), Input("sdr-table-platform", "value")],
)
def gen_sdr_table(pagination_settings, value):
    data = app.sdr_subscriber.sdrs
    data = data.loc[data["platform_name"] == value]
    data = data.sort_index(ascending=False)
    start = pagination_settings["current_page"] * pagination_settings["page_size"]
    end = (pagination_settings["current_page"] + 1) * pagination_settings["page_size"]
    data = data.iloc[start:end]
    data["delay_min"] = data["delay"] / pd.Timedelta("60 seconds")
    data["delay_min"] = data["delay_min"].astype("int64")
    data["start_time_str"] = data["start_time"].dt.strftime("%b %-d %H:%M:%S")
    data["aquisition time"] = data.index.to_series().dt.strftime("%b %-d %H:%M:%S")
    data["age"] = pd.to_datetime("now") - data["start_time"]
    data["age"] = data["age"] / pd.Timedelta("60 seconds")
    data["age"] = data["age"].astype("int64")
    return data.to_dict("records")


@app.callback(
    [
        Output("data-arrival-indicator", "className"),
        Output("data-arrival-indicator", "title"),
    ],
    [Input("data-arrival-indicator-update", "n_intervals")],
)
def update_data_arrival_indicator(n_intervals):
    pdnow = pd.to_datetime("now")
    yesterday = pdnow - pd.Timedelta("1 days")
    today_data = app.sdr_subscriber.sdrs[yesterday:pdnow]
    today_data = len(today_data)

    data = app.sdr_subscriber.sdrs
    days = data.index.max() - data.index.min()
    days = days / pd.Timedelta("1 days")
    data = len(data)
    if days > 0:
        data = data / days

    yellow = int(data * 0.9)
    red = int(data * 0.5)

    if today_data > yellow:
        className = "fa fa-star"
        title = "{} files today; yellow threashold is {}".format(today_data, yellow)
    elif today_data > red:
        className = "fa fa-warning"
        title = "{} files today; yellow threashold is {}, red threashold is {}".format(
            today_data, yellow, red
        )
    else:
        className = "fa fa-exclamation-circle"
        title = "{} files today; red threashold is {}".format(today_data, red)

    return className, title
