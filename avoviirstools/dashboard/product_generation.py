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


@app.callback(
    [
        Output("product-generation-indicator", "style"),
        Output("product-generation-indicator", "className"),
    ],
    [Input("product-generation-indicator-update", "n_intervals")],
)
def update_product_generation_indicator(value):
    tasks_waiting = update_subscriber.updates[-1]

    if tasks_waiting < 6:
        color = "#49B52C"
        className = "fa fa-star"
    elif tasks_waiting < 10:
        color = "#D8BC35"
        className = "fa fa-warning"
    else:
        color = "#D84435"
        className = "fa fa-exclamation-circle"

    style = {"padding": "5px", "color": color}
    return style, className
