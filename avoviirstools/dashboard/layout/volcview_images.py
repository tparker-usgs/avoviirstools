import dash_html_components as html
import dash_core_components as dcc
import dash_table


def volcview_images_layout():
    return html.Div(
        [
            html.Div(
                [html.Div([volcview_label()]), volcview_images_pane()], className="col"
            )
        ],
        id="volcview-images-pane",
        className="row dashboard-pane",
    )


def volcview_label():
    return html.Label(
        [
            html.H2(
                [
                    html.A(
                        html.I(
                            className="fa fa-question-circle",
                            id="volcview-images-indicator",
                        ),
                        target="help",
                        href="/assets/help.html#volcview-images-indicator",
                        className="indicator",
                    ),
                    "Volcview Images",
                ]
            ),
            dcc.Interval(
                id="volcview-images-indicator-update", interval=5000, n_intervals=0
            ),
        ],
        htmlFor="volcview-images-pane",
    )


def volcview_sectors():
    return html.Div(
        [
            html.Label(html.H5("Images by Sector"), htmlFor="volcview-products"),
            html.I(className="fa fa-refresh", id="volcview-sectors-update"),
            html.A(
                html.I(className="fa fa-question", id="volcview-sectors-help"),
                className="help",
                target="help",
                href="/assets/help.html#volcview-sectors",
            ),
            dcc.Graph(
                id="volcview-sectors",
                className="avo-dash-element",
                config={
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d"],
                },
            ),
        ]
    )


def volcview_products():
    return html.Div(
        [
            html.Label(html.H5("Images by Product"), htmlFor="volcview-products"),
            html.I(className="fa fa-refresh", id="volcview-products-update"),
            html.A(
                html.I(className="fa fa-question", id="volcview-products-help"),
                target="help",
                href="/assets/help.html#volcview-products",
            ),
            dcc.Graph(
                id="volcview-products",
                className="avo-dash-element",
                config={
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d"],
                },
            ),
        ]
    )


def volcview_table():
    return html.Div(
        [
            html.Label(html.H5("Last 50 Images"), htmlFor="volcview-table"),
            html.I(className="fa fa-refresh", id="volcview-table-update"),
            html.A(
                html.I(className="fa fa-question", id="volcview-table--help"),
                target="help",
                href="/assets/help.html#volcview-table",
            ),
            dash_table.DataTable(
                id="volcview-table",
                columns=[
                    {"name": "Image Time", "id": "image time"},
                    {"name": "Data Time", "id": "data time"},
                    {"name": "Sector", "id": "sector"},
                    {"name": "Product", "id": "band"},
                ],
                n_fixed_rows=1,
                style_as_list_view=True,
                style_cell={"padding": "5px"},
                style_table={
                    "maxHeight": "450px",
                    "overflowY": "scroll",
                    "border": "thin lightgrey solid",
                },
                css=[
                    {
                        "selector": ".dash-cell div.dash-cell-value",
                        "rule": "display: inline; white-space: inherit;"
                        "overflow: inherit; text-overflow: inherit;",
                    }
                ],
            ),
        ]
    )


def volcview_images_pane():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [volcview_sectors()],
                                className="col",
                                style={"margin": "20px"},
                            )
                        ],
                        className="row",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [volcview_products()],
                                className="col",
                                style={"margin": "20px"},
                            )
                        ],
                        className="row",
                    ),
                ],
                className="col-4",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [volcview_table()],
                                className="col",
                                style={"margin": "20px"},
                            )
                        ],
                        className="row",
                    )
                ],
                className="col-8",
            ),
        ],
        className="row align-items-right",
    )
