from dash.dependencies import Input, Output

from .. import app
import pandas as pd

YELLOW_THREASHOLD = 0.9
RED_THREASHOLD = 0.5


@app.callback(
    Output("volcview-sectors", "figure"), [Input("volcview-sectors-update", "n_clicks")]
)
def gen_volcview_sectors(n_clicks):
    pdnow = pd.to_datetime("now")
    yesterday = pdnow - pd.Timedelta("1 days")
    today_data = app.sector_subscriber.sector_images[yesterday:pdnow]
    today_data = today_data.groupby("sector").size()

    data = app.sector_subscriber.sector_images
    days = data.index.max() - data.index.min()
    days = days / pd.Timedelta("1 days")
    data = data.groupby("sector").size()
    if days > 0:
        data = data / days

    return {
        "data": [
            {"x": today_data.index, "y": today_data, "type": "bar", "name": "today"},
            {
                "x": data.index,
                "y": data,
                "type": "scatter",
                "name": "average",
                "mode": "markers",
            },
        ]
    }


@app.callback(
    Output("volcview-products", "figure"),
    [Input("volcview-products-update", "n_clicks")],
)
def gen_volcview_products(n_clicks):
    pdnow = pd.to_datetime("now")
    yesterday = pdnow - pd.Timedelta("1 days")
    today_data = app.sector_subscriber.sector_images[yesterday:pdnow]
    today_data = today_data.groupby("band").size()

    data = app.sector_subscriber.sector_images
    days = data.index.max() - data.index.min()
    days = days / pd.Timedelta("1 days")
    data = data.groupby("band").size()
    if days > 0:
        data = data / days

    return {
        "data": [
            {"x": today_data.index, "y": today_data, "type": "bar", "name": "today"},
            {
                "x": data.index,
                "y": data,
                "type": "scatter",
                "name": "average",
                "mode": "markers",
            },
        ]
    }


@app.callback(
    Output("volcview-table", "data"), [Input("volcview-table", "pagination_settings")]
)
def gen_sdr_table(pagination_settings):
    data = app.sector_subscriber.sector_images
    data = data.sort_index(ascending=False)
    start = pagination_settings["current_page"] * pagination_settings["page_size"]
    end = (pagination_settings["current_page"] + 1) * pagination_settings["page_size"]
    data = data.iloc[start:end]
    data["time"] = data.index.to_series().dt.strftime("%b %-d %H:%M:%S")
    return data.to_dict("records")


@app.callback(
    [
        Output("volcview-images-indicator", "className"),
        Output("volcview-images-indicator", "title"),
    ],
    [Input("volcview-images-indicator-update", "n_intervals")],
)
def update_volcview_images_indicator(value):
    pdnow = pd.to_datetime("now")
    yesterday = pdnow - pd.Timedelta("1 days")
    today_data = app.sector_subscriber.sector_images[yesterday:pdnow]
    today_data = len(today_data)

    data = app.sector_subscriber.sector_images
    days = data.index.max() - data.index.min()
    days = days / pd.Timedelta("1 days")
    data = len(data)
    if days > 0:
        data = int(data / days)

    yellow = int(data * 0.9)
    red = int(data * 0.5)

    if today_data > yellow:
        className = "fa fa-star"
        tooltip = "{} images today; yellow threashold is {}".format(today_data, yellow)
    elif today_data > red:
        className = "fa fa-warning"
        tooltip = "{} images today; yellow threashold {}, red threshold {}".format(
            today_data, yellow, red
        )
    else:
        className = "fa fa-exclamation-circle"
        tooltip = "{} images today; red threashold is {}".format(today_data, red)

    return className, tooltip
