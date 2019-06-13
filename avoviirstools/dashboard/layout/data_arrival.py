import dash_html_components as html
import dash_core_components as dcc
import dash_table


def data_arrival_layout():
    return html.Div(
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
                                            id="data-arrival-indicator",
                                        ),
                                        target="help",
                                        href="/assets/help.html#data-arrival-indicator",
                                        className="indicator",
                                    ),
                                    "Data Arrival",
                                ]
                            ),
                            dcc.Interval(
                                id="data-arrival-indicator-update",
                                interval=5000,
                                n_intervals=0,
                            ),
                        ],
                        htmlFor="data-arrival-pane",
                    ),
                    data_arrival_pane(),
                ],
                className="col",
            )
        ],
        id="data-arrival-pane",
        className="row dashboard-pane",
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
            html.Label(html.H5("Last Seen"), htmlFor="last-seen-table"),
            html.I(className="fa fa-refresh", id="last-seen-table-update"),
            html.A(
                html.I(className="fa fa-question", id="last-seen-table-help"),
                target="help",
                href="/assets/help.html#last-seen-table",
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
                html.H5("Acquisition Delay (min)"), htmlFor="datafile-latency-table"
            ),
            html.I(className="fa fa-refresh", id="datafile-latency-update"),
            html.A(
                html.I(className="fa fa-question", id="datafile-latency-help"),
                target="help",
                href="/assets/help.html#datafile-latency",
            ),
            dcc.Graph(id="datafile-latency", className="avo-dash-element"),
        ],
        style={"margin": "50px"},
    )


def datafile_gap():
    return html.Div(
        [
            html.Label(html.H5("Interfile Gap (min)"), htmlFor="datafile-gap"),
            html.I(className="fa fa-refresh", id="datafile-gap-update"),
            html.A(
                html.I(className="fa fa-question", id="datafile-gap-help"),
                target="help",
                href="/assets/help.html#datafile-gap",
            ),
            dcc.Graph(id="datafile-gap", className="avo-dash-element"),
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
            html.Label(html.H5("Last 100 Datafiles"), htmlFor="sdr-table-platform"),
            html.I(className="fa fa-refresh", id="sdr-table-update"),
            html.A(
                html.I(className="fa fa-question", id="sdr-table--help"),
                target="help",
                href="/assets/help.html#sdr-table",
            ),
            dcc.Dropdown(
                id="sdr-table-platform",
                options=[{"label": i, "value": i} for i in ["Suomi-NPP", "NOAA-20"]],
                value="Suomi-NPP",
                searchable=False,
                clearable=False,
                style={"position": "relative", "zIndex": "999"},
            ),
            dash_table.DataTable(
                id="sdr-table",
                columns=columns,
                column_static_tooltip=tooltips,
                style_as_list_view=True,
                style_header={"whiteSpace": "normal"},
                style_cell={"padding": "10px"},
                n_fixed_rows=1,
                style_table={
                    "maxHeight": "300px",
                    "overflowY": "scroll",
                    "border": "thin lightgrey solid",
                },
                # css=[
                # {
                # "selector": ".dash-cell div.dash-cell-value",
                # "box-sizing": "inherit",
                # "rule": "display: inline; white-space: inherit;"
                # " overflow: inherit; text-overflow: inherit;",
                # }
                # ],
            ),
        ]
    )
