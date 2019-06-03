from dash.dependencies import Input, Output
from .update_subscriber import UpdateSubscriber
from .app import zmq_context, app
import pandas as pd

update_subscriber = UpdateSubscriber(zmq_context)


class ProductGeneration:
    def __init__(self):
        update_subscriber.start()

    def flush(self):
        update_subscriber.flush()


@app.callback(
    Output("products-waiting", "figure"),
    [Input("products-waiting-update", "n_intervals")],
)
def gen_products_waiting(interval):
    waiting_tasks = update_subscriber.updates
    figure = {
        "data": [
            {
                "x": waiting_tasks.index,
                "y": waiting_tasks,
                "type": "scatter",
                "name": "Products Waiting",
                "fill": "tozeroy",
            }
        ],
        "layout": {"xaxis": {"type": "date", "rangemode": "nonnegative"}},
    }

    return figure


@app.callback(
    Output("products-waiting-update", "disabled"),
    [Input("products-waiting-auto", "values")],
)
def update_refresh(auto_values):
    return "Auto" not in auto_values


@app.callback(
    Output("product-generation-indicator", "style"),
    [Input("product-generation-indicator-update", "n_intervals")],
)
def update_product_generation_indicator(value):
    pdnow = pd.to_datetime("now")
    yesterday = pdnow - pd.Timedelta("1 days")

    today_tasks = update_subscriber.updates[yesterday:pdnow]
    today_tasks = today_tasks.size

    all_tasks = update_subscriber.updates

    days = all_tasks.index.max() - all_tasks.index.min()
    days = days / pd.Timedelta("1 days")
    all_tasks = all_tasks.size
    if days > 0:
        all_tasks = all_tasks / days

    coverage = today_tasks / all_tasks

    if coverage > 0.9:
        color = "#49B52C"
    elif coverage > 0.5:
        color = "#D8BC35"
    else:
        color = "#D84435"
    print("returning color: {}".format(color))
    return {"padding": "5px", "color": color}
