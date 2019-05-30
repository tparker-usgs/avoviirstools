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
            html.Div([html.H3("Volcview Sectors")], className="row bg-secondary"),
            html.Div([html.H3("Product Generation")], className="row bg-secondary"),
            product_generation_pane(),
            html.Div([html.H3("Data Arrival")], className="row bg-secondary"),
            data_arrival_pane(),
        ],
        className="container-fluid",
    )
    print("TOMP SAYS IN LAYOUT: {}".format(app))


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
    return dash_table.DataTable(
        id="last-seen-table",
        columns=[
            {"name": "", "id": "platform"},
            {"name": "Last Seen", "id": "last seen"},
        ],
        style_as_list_view=True,
        style_table={"width": "300px", "margin": "0px auto"},
    )


def datafile_latency():
    return dcc.Graph(
        id="datafile-latency",
        style={"height": "300px"},
        figure={
            "layout": {
                "xaxis": {"type": "date"},
                "yaxis": {"title": "SDR Latency minutes"},
            }
        },
    )


def datafile_gap():
    return dcc.Graph(id="datafile-gap", style={"height": "300px"})


def datafile_table():
    columns = [
        {"name": "orbit", "id": "orbit_number"},
        {"name": "segment", "id": "segment"},
        {"name": "data start", "id": "start_time_str"},
        {"name": "aquisition time", "id": "aquisition time"},
        {"name": "AVO aquisition delay (min)", "id": "delay"},
        {"name": "data age (min)", "id": "age"},
    ]

    tooltips = {
        "aquisition time": "When did the data arrive at AVO?",
        "delay": "How long did it take for the data to arrive at AVO?",
        "age": "How old is the data?",
    }

    return dash_table.DataTable(
        id="sdr-table",
        columns=columns,
        column_static_tooltip=tooltips,
        pagination_settings={"current_page": 0, "page_size": 12},
        pagination_mode="fe",
        style_table={"maxHeight": "700px"},
        style_as_list_view=True,
        style_header={"minWidth": "0px", "maxWidth": "250px", "whiteSpace": "normal"},
        style_cell={"padding": "10px"},
        css=[
            {
                "selector": ".dash-cell div.dash-cell-value",
                "rule": "display: inline; white-space: inherit;"
                " overflow: inherit; text-overflow: inherit;",
            }
        ],
    )
