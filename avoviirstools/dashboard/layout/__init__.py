import dash_html_components as html
from .volcview_images import volcview_images_layout
from .product_generation import product_generation_layout
from .data_arrival import data_arrival_layout


def gen_layout():
    return html.Div(
        [
            html.Div(
                [html.H1("AVO VIIRS Processing")],
                className="row justify-content-center",
            ),
            volcview_images_layout(),
            product_generation_layout(),
            data_arrival_layout(),
        ],
        className="container-fluid",
    )
