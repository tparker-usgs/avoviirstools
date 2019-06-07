emport dash_html_components as html
import dash_core_components as dcc
import dash_table


def volcview_images_layout():
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
                                                    id="volcview-images-indicator",
                                                    style={
                                                        "padding": "5px",
                                                        "color": "#E8EAEE",
                                                    },
                                                ),
                                                target="help",
                                                href="/assets/help.html#volcview-images-indicator",
                                            ),
                                            "Volcview Images",
                                        ]
                                    ),
                                    dcc.Interval(
                                        id="volcview-images-indicator-update",
                                        interval=5000,
                                        n_intervals=0,
                                    ),
                                ],
                                htmlFor="volcview-images-pane",
                            )
                        ]
                    ),
                    volcview_images_pane(),
                ],
                className="col",
            )
        ],
        id="volcview-images-pane",
        className="row dashboard-pane",
    )


def volcview_sectors():
    return html.Div(
        [
            html.Label(html.H5("Images by Sector"), htmlFor="volcview-products"),
            html.I(
                className="fa fa-refresh",
                id="volcview-sectors-update",
                style={"padding": "5px"},
            ),
            html.A(
                html.I(
                    className="fa fa-question",
                    id="volcview-sectors-help",
                    style={"padding": "5px"},
                ),
                className="help",
                target="help",
                href="/assets/help.html#volcview-sectors",
            ),
            dcc.Graph(id="volcview-sectors", style={"height": "300px"}),
        ]
    )


def volcview_products():
    return html.Div(
        [
            html.Label(html.H5("Images by Product"), htmlFor="volcview-products"),
            html.I(
                className="fa fa-refresh",
                id="volcview-products-update",
                style={"padding": "5px"},
            ),
            html.A(
                html.I(
                    className="fa fa-question",
                    id="volcview-products-help",
                    style={"padding": "5px"},
                ),
                target="help",
                href="/assets/help.html#volcview-products",
            ),
            dcc.Graph(id="volcview-products", style={"height": "300px"}),
        ]
    )


def volcview_table():
    return html.Div(
        [
            html.Label(html.H5("Recent Images"), htmlFor="volcview-table"),
            html.A(
                html.I(
                    className="fa fa-question",
                    id="volcview-table--help",
                    style={"padding": "5px"},
                ),
                target="help",
                href="/assets/help.html#volcview-table",
            ),
            dash_table.DataTable(
                id="volcview-table",
                columns=[
                    {"name": "Time", "id": "time"},
                    {"name": "Sector", "id": "sector"},
                    {"name": "Product", "id": "band"},
                ],
                style_as_list_view=True,
                pagination_settings={"current_page": 0, "page_size": 7},
                pagination_mode="be",
                style_cell={"padding": "10px"},
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
            html.Div([volcview_sectors()], className="col-5"),
            html.Div([volcview_products()], className="col-4"),
            html.Div([volcview_table()], className="col-3"),
        ],
        className="row align-items-right",
    )
