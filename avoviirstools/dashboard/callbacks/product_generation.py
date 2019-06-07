from dash.dependencies import Input, Output
from .. import app

YELLOW_THRESHOLD = 6
RED_THRESHOLD = 10


@app.callback(
    Output("products-waiting", "figure"),
    [Input("products-waiting-update", "n_intervals")],
)
def gen_products_waiting(interval):
    waiting_tasks = app.update_subscriber.updates
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
def update_products_waiting_refresh(auto_values):
    return "Auto" not in auto_values


@app.callback(
    [
        Output("product-generation-indicator", "className"),
        Output("product-generation-indicator", "title"),
    ],
    [Input("product-generation-indicator-update", "n_intervals")],
)
def update_product_generation_indicator(value):
    tasks_waiting = app.update_subscriber.updates[-1]

    if tasks_waiting < YELLOW_THRESHOLD:
        className = "fa fa-star"
        tooltip = "{} products waiting; yellow threashold {}".format(
            tasks_waiting, YELLOW_THRESHOLD
        )
    elif tasks_waiting < RED_THRESHOLD:
        className = "fa fa-warning"
        tooltip = "{} products waiting; green threashold {}, red threshold {}".format(
            tasks_waiting, YELLOW_THRESHOLD, RED_THRESHOLD
        )
    else:
        className = "fa fa-exclamation-circle"
        tooltip = "{} products waiting; yellow threshold {}".format(
            tasks_waiting, YELLOW_THRESHOLD, RED_THRESHOLD
        )

    return className, tooltip
