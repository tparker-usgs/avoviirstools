from dash.dependencies import Input, Output
from .update_subscriber import UpdateSubscriber
from .app import zmq_context, app

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
