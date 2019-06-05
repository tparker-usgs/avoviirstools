import dash_html_components as html
import dash_core_components as dcc
import dash_table

from .volcview_images_layout import volcview_images_layout
from .product_generation_layout import product_generation_layout
from .data_arrival_layout import data_arrival_layout


def gen_layout():
    layout = html.Div(
        [volcview_images_layout(), product_generation_layout(), data_arrival_layout()],
        className="container-fluid",
    )
    return layout
