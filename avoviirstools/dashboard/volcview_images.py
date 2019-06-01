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
    days = days.days
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
        ],
        "layout": {"title": "Images by Sector"},
    }

@app.callback(
    Output("volcview-products", "figure"),
    [Input("volcview-products-update", "n_clicks")],
)
def gen_volcview_products(n_clicks):
    pdnow = pd.to_datetime("now")
    yesterday = pdnow - pd.Timedelta("1 days")
    today_data = sector_subscriber.sector_images[yesterday:pdnow]
    today_data = today_data.groupby("sector").size()

    data = sector_subscriber.sector_images
    days = data.index.max() - data.index.min()
    days = days.days
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
        ],
        "layout": {"title": "Images by Product"},
    }

