import dash_html_components as html
import dash_core_components as dcc
import dash_table

from .app import app


def apply_layout():
    app.layout = html.Div(
        [
            html.Div(
                [html.H1("AVO VIIRS Processing")],
                className="row justify-content-center bg-primary",
            ),
            html.Div([html.H3("Volcview Images")], className="row bg-secondary"),
            volcview_images_pane(),
            html.Div([html.H3("Product Generation")], className="row bg-secondary"),
            product_generation_pane(),
            html.Div([html.H3("Data Arrival")], className="row bg-secondary"),
            data_arrival_pane(),
        ],
        className="container-fluid",
    )


def volcview_images_pane():
    return html.Div(
        [
            dcc.Graph(id="volcview-sectors", style={"height": "300px"}),
            html.Button("Update", id="volcview-sectors-update"),
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
        className="row justify-content-center",
    )


def last_seen_table():
    return html.Div(
        [
            dash_table.DataTable(
                id="last-seen-table",
                columns=[
                    {"name": "", "id": "platform"},
                    {"name": "Last Seen", "id": "last seen"},
                ],
                style_as_list_view=True,
                style_table={"width": "300px", "margin": "0px auto"},
            ),
            html.Button("Update", id="last-seen-table-update"),
        ]
    )


def datafile_latency():
    return html.Div(
        [
            dcc.Graph(id="datafile-latency", style={"height": "300px"}),
            html.Button("Update", id="datafile-latency-update"),
        ]
    )


def datafile_gap():
    return html.Div(
        [
            dcc.Graph(id="datafile-gap", style={"height": "300px"}),
            html.Button("Update", id="datafile-gap-update"),
        ]
    )


def datafile_table():
    columns = [
        {"name": "Orbit", "id": "orbit_number"},
        {"name": "Segment", "id": "segment"},
        {"name": "Start", "id": "start_time_str"},
        {"name": "Arrival Time", "id": "aquisition time"},
        {"name": "AVO Acquisition Delay (min)", "id": "delay_min"},
        {"name": "Data Age (min)", "id": "age"},
    ]

    tooltips = {
        "aquisition time": "When did the data arrive at AVO?",
        "delay": "How long did it take for the data to arrive at AVO?",
        "age": "How old is the data?",
    }

    return html.Div(
        [
            dcc.RadioItems(
                id="sdr-table-platform",
                options=[{"label": i, "value": i} for i in ["Suomi-NPP", "NOAA-20"]],
                value="Suomi-NPP",
                labelStyle={"display": "inline-block"},
            ),
            dash_table.DataTable(
                id="sdr-table",
                columns=columns,
                column_static_tooltip=tooltips,
                pagination_settings={"current_page": 0, "page_size": 15},
                pagination_mode="be",
                style_table={"maxHeight": "700px"},
                style_as_list_view=True,
                style_header={
                    "minWidth": "0px",
                    "maxWidth": "250px",
                    "whiteSpace": "normal",
                },
                style_cell={"padding": "10px"},
                css=[
                    {
                        "selector": ".dash-cell div.dash-cell-value",
                        "rule": "display: inline; white-space: inherit;"
                        " overflow: inherit; text-overflow: inherit;",
                    }
                ],
            ),
        ]
    )
