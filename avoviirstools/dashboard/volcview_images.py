from dash.dependencies import Input, Output
from .sector_subscriber import SectorSubscriber
from .app import zmq_context, app
import pandas as pd


sector_subscriber = SectorSubscriber(zmq_context)


class VolcviewImages:
    def __init__(self):
        sector_subscriber.start()

    def flush(self):
        sector_subscriber.flush()


@app.callback(
    Output("volcview-sectors", "figure"), [Input("volcview-sectors-update", "n_clicks")]
)
def gen_volcview_sectors(n_clicks):
    pdnow = pd.to_datetime("now")
    yesterday = pdnow - pd.Timedelta("1 days")
    today_data = sector_subscriber.sector_images[yesterday:pdnow]
    today_data = today_data.groupby("sector").size()

    data = sector_subscriber.sector_images
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
    today_data = sector_subscriber.sector_images[yesterday:pdnow]
    today_data = today_data.groupby("band").size()

    data = sector_subscriber.sector_images
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
    data = sector_subscriber.sector_images
    data = data.sort_index(ascending=False)
    start = pagination_settings["current_page"] * pagination_settings["page_size"]
    end = (pagination_settings["current_page"] + 1) * pagination_settings["page_size"]
    data = data.iloc[start:end]
    data["time"] = data.index.to_series().dt.strftime("%b %-d %H:%M:%S")
    return data.to_dict("records")


@app.callback([
    Output("volcview-images-indicator", "style"),Output("volcview-images-indicator", "className")],
    [Input("volcview-images-indicator-update", "n_intervals")],
)
def update_volcview_images_indicator(value):
    pdnow = pd.to_datetime("now")
    yesterday = pdnow - pd.Timedelta("1 days")
    today_data = sector_subscriber.sector_images[yesterday:pdnow]
    today_data = len(today_data)

    data = sector_subscriber.sector_images
    days = data.index.max() - data.index.min()
    days = days / pd.Timedelta("1 days")
    data = len(data)
    if days > 0:
        data = data / days

    coverage = today_data / data

    if coverage > 0.9:
        color = "#49B52C"
        className = "fa fa-star"
    elif coverage > 0.5:
        color = "#D8BC35"
        className = "fa fa-warning"
    else:
        color = "#D84435"
        className = "fa fa-star"
        className = "fa fa-exclamation-circle"

    style = {"padding": "5px", "color": color}
                                                         
    return style, className
