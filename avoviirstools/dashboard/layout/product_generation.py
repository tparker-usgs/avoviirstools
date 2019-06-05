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
                                            html.I(
                                                className="fa fa-question-circle",
                                                id="product-generation-indicator",
                                                style={
                                                    "padding": "5px",
                                                    "color": "#E8EAEE",
                                                },
                                            ),
                                            "Product Generation",
                                        ],
                                        style={"fontFamily": "Merriweather"},
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
                className="row",
                style={
                    "backgroundColor": "#E8EAEE",
                    "borderRadius": "5px",
                    "border": "2px solid #687696",
                    "padding": "20px",
                    "margin": "20px",
                },
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
                    html.Label(
                        html.H5(
                            "Products Waiting", style={"fontFamily": "Merriweather"}
                        ),
                        htmlFor="products-waiting",
                    ),
                    html.I(
                        className="fa fa-question",
                        id="products-waiting-help",
                        style={"padding": "5px"},
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
