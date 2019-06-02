import dash_html_components as html
import dash_core_components as dcc
import dash_table

from .app import app


def apply_layout():
    app.layout = html.Div(
        [
            html.Div(
                [html.H1("AVO VIIRS Processing", style={"fontFamily": "Merriweather"})],
                className="row justify-content-center",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label(
                                html.H2(
                                    "Volcview Images",
                                    style={"fontFamily": "Merriweather"},
                                ),
                                htmlFor="volcview-images-pane",
                            ),
                            volcview_images_pane(),
                        ],
                        className="col",
                    )
                ],
                id="volcview-images-pane",
                className="row",
                style={
                    "backgroundColor": "#D1EF9F",
                    "borderRadius": "5px",
                    "border": "2px solid #446906",
                    "padding": "20px",
                    "margin": "20px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label(
                                html.H2(
                                    "Product Generation",
                                    style={"fontFamily": "Merriweather"},
                                ),
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
                    "backgroundColor": "#D1EF9F",
                    "borderRadius": "5px",
                    "border": "2px solid #446906",
                    "padding": "20px",
                    "margin": "20px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label(
                                html.H2(
                                    "Data Arrival", style={"fontFamily": "Merriweather"}
                                ),
                                htmlFor="data-arrival-pane",
                            ),
                            data_arrival_pane(),
                        ],
                        className="col",
                    )
                ],
                id="data-arrival-pane",
                className="row",
                style={
                    "backgroundColor": "#D1EF9F",
                    "borderRadius": "5px",
                    "border": "2px solid #446906",
                    "padding": "20px",
                    "margin": "20px",
                },
            ),
        ],
        className="container-fluid",
    )


def volcview_sectors():
    return html.Div(
        [
            html.Label(
                html.H5("Images by Sector", style={"fontFamily": "Merriweather"}),
                htmlFor="volcview-products",
            ),
            html.I(
                className="fa fa-refresh",
                id="volcview-sectors-update",
                style={"padding": "5px"},
            ),
            html.I(
                className="fa fa-question",
                id="volcview-sectors-help",
                style={"padding": "5px"},
            ),
            dcc.Graph(id="volcview-sectors", style={"height": "300px"}),
        ]
    )


def volcview_products():
    return html.Div(
        [
            html.Label(
                html.H5("Images by Product", style={"fontFamily": "Merriweather"}),
                htmlFor="volcview-products",
            ),
            html.I(
                className="fa fa-refresh",
                id="volcview-products-update",
                style={"padding": "5px"},
            ),
            html.I(
                className="fa fa-question",
                id="volcview-products-help",
                style={"padding": "5px"},
            ),
            dcc.Graph(id="volcview-products", style={"height": "300px"}),
        ]
    )


def volcview_table():
    return html.Div(
        [
            html.Label(
                html.H5("Recent Images", style={"fontFamily": "Merriweather"}),
                htmlFor="volcview-table",
            ),
            html.I(
                className="fa fa-question",
                id="volcview-table--help",
                style={"padding": "5px"},
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


def data_arrival_pane():
    return html.Div(
        [
            html.Div(
                [last_seen_table(), datafile_latency(), datafile_gap()],
                className="col-5",
            ),
            html.Div([datafile_table()], className="col-7"),
        ],
        className="row",
    )


def last_seen_table():
    return html.Div(
        [
            html.Label(
                html.H5("Last Seen", style={"fontFamily": "Merriweather"}),
                htmlFor="last-seen-table",
            ),
            html.I(
                className="fa fa-refresh",
                id="last-seen-table-update",
                style={"padding": "5px"},
            ),
            html.I(
                className="fa fa-question",
                id="last-seen-table-help",
                style={"padding": "5px"},
            ),
            dash_table.DataTable(
                id="last-seen-table",
                columns=[
                    {"name": "", "id": "platform"},
                    {"name": "Last Seen", "id": "last seen"},
                ],
                style_as_list_view=True,
                style_table={"width": "300px", "margin": "0px auto"},
            ),
        ],
        style={"margin": "50px"},
    )


def datafile_latency():
    return html.Div(
        [
            html.Label(
                html.H5(
                    "Acquisition Delay (min)", style={"fontFamily": "Merriweather"}
                ),
                htmlFor="datafile-latency-table",
            ),
            html.I(
                className="fa fa-refresh",
                id="datafile-latency-update",
                style={"padding": "5px"},
            ),
            html.I(
                className="fa fa-question",
                id="datafile-latency-help",
                style={"padding": "5px"},
            ),
            dcc.Graph(id="datafile-latency", style={"height": "300px"}),
        ],
        style={"margin": "50px"},
    )


def datafile_gap():
    return html.Div(
        [
            html.Label(
                html.H5("Interfile Gap (min)", style={"fontFamily": "Merriweather"}),
                htmlFor="datafile-gap",
            ),
            html.I(
                className="fa fa-refresh",
                id="datafile-gap-update",
                style={"padding": "5px"},
            ),
            html.I(
                className="fa fa-question",
                id="datafile-gap-help",
                style={"padding": "5px"},
            ),
            dcc.Graph(id="datafile-gap", style={"height": "300px"}),
        ],
        style={"margin": "50px"},
    )


def datafile_table():
    columns = [
        {"name": "Orbit", "id": "orbit_number"},
        {"name": "Segment", "id": "segment"},
        {"name": "Start", "id": "start_time_str"},
        {"name": "Arrival Time", "id": "aquisition time"},
        {"name": "Delay (min)", "id": "delay_min"},
        {"name": "Age (min)", "id": "age"},
    ]

    tooltips = {
        "aquisition time": "When did the data arrive at AVO?",
        "delay": "How long did it take for the data to arrive at AVO?",
        "age": "How old is the data?",
    }

    return html.Div(
        [
            html.Label(
                html.H5("Recent Datafiles", style={"fontFamily": "Merriweather"}),
                htmlFor="sdr-table-platform",
            ),
            html.I(
                className="fa fa-question",
                id="sdr-table--help",
                style={"padding": "5px"},
            ),
            dcc.Dropdown(
                id="sdr-table-platform",
                options=[{"label": i, "value": i} for i in ["Suomi-NPP", "NOAA-20"]],
                value="Suomi-NPP",
                searchable=False,
                clearable=False,
            ),
            dash_table.DataTable(
                id="sdr-table",
                columns=columns,
                column_static_tooltip=tooltips,
                pagination_settings={"current_page": 0, "page_size": 15},
                pagination_mode="be",
                style_table={"maxHeight": "700px"},
                style_as_list_view=True,
                style_header={"whiteSpace": "normal"},
                style_cell={"padding": "10px"},
                css=[
                    {
                        # "selector": ".dash-cell div.dash-cell-value",
                        # "box-sizing": "inherit",
                        # "rule": "display: inline; white-space: inherit;"
                        # " overflow: inherit; text-overflow: inherit;",
                    }
                ],
            ),
        ]
    )
