"""Dash layout construction for the browser app."""

from __future__ import annotations

from dash import dcc, html

from .config import BAD_CHANNELS_ID, BROWSER_DATA_ID, BROWSER_GRAPH_ID, CHANNEL_SLIDER_ID


def build_layout(
    *,
    initial_figure,
    client_data: dict,
    max_slider_value: int,
    slider_start: int,
):
    """Build the top-level Dash layout."""
    return html.Div(
        style={"display": "flex", "alignItems": "flex-start", "columnGap": "8px"},
        children=[
            dcc.Store(id=BROWSER_DATA_ID, data=client_data),
            dcc.Store(id=BAD_CHANNELS_ID, data=client_data["bads"]),
            html.Div(
                children=[
                    dcc.Slider(
                        id=CHANNEL_SLIDER_ID,
                        min=0,
                        max=max_slider_value,
                        step=1,
                        value=slider_start,
                        marks=None,
                        vertical=True,
                        verticalHeight=300,
                        included=False,
                        updatemode="drag",
                    )
                ],
                style={"width": "2%", "paddingTop": "10%", "flexShrink": 0},
            ),
            html.Div(
                children=[dcc.Graph(id=BROWSER_GRAPH_ID, figure=initial_figure)],
                style={"flex": "1 1 auto", "minWidth": 0},
            ),
        ],
    )
