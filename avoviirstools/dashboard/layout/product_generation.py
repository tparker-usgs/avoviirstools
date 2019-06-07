import dash_html_components as html
import dash_core_components as dcc


def product_generation_layout():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Label(
                                [
                                    html.H2(
                                        [
                                            html.A(
                                                html.I(
                                                    className="fa fa-question-circle",
                                                    id="product-generation-indicator",
                                                ),
                                                target="help",
                                                href="/assets/help.html#product-generation-indicator",
                                                className="indicator",
                                            ),
                                            "Product Generation",
                                        ]
                                    ),
                                    dcc.Interval(
                                        id="product-generation-indicator-update",
                                        interval=5000,
                                        n_intervals=0,
                                    ),
                                ],
                                htmlFor="product-generation-pane",
                            ),
                            product_generation_pane(),
                        ],
                        className="col",
                    )
                ],
                id="product-generation-pane",
                className="row dashboard-pane",
            )
        ]
    )


def product_generation_pane():
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
                    html.Label(html.H5("Products Waiting"), htmlFor="products-waiting"),
                    html.A(
                        html.I(className="fa fa-question", id="products-waiting-help"),
                        target="help",
                        href="/assets/help.html#products-waiting",
                    ),
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
