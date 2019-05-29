import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from .update_subscriber import UpdateSubscriber
from .app import zmq_context, app


class ProductGeneration:
    def __init__(self):
        self.update_subscriber = UpdateSubscriber(zmq_context)
        self.update_subscriber.start()

    def fluch(self):
        self.update_subscriber.flush()

    def product_generation_pane(self):
        return html.Div(
            [
                dcc.Checklist(
                    id="products-waiting-auto",
                    options=[{"label": "Auto Update", "value": "Auto"}],
                    values=["Auto"],
                    className="col-auto",
                ),
                html.Div(
                    [
                        dcc.Graph(id="products-waiting", style={"height": "350px"}),
                        dcc.Interval(
                            id="products-waiting-update", interval=5000, n_intervals=0
                        ),
                    ],
                    className="col",
                ),
            ],
            className="row align-items-center",
        )

    @app.callback(
        Output("products-waiting", "figure"),
        [Input("products-waiting-update", "n_intervals")],
    )
    def gen_products_waiting(self, interval):
        waiting_tasks = self.update_subscriber.updates
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
            "layout": {
                "xaxis": {"type": "date", "rangemode": "nonnegative"},
                "title": "Products waiting to be generated",
            },
        }

        return figure

    @app.callback(
        Output("products-waiting-update", "disabled"),
        [Input("products-waiting-auto", "values")],
    )
    def update_refresh(auto_values):
        return "Auto" not in auto_values
