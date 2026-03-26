"""Dash callback registration for browser interactivity."""

from __future__ import annotations

from dash import ClientsideFunction, Input, Output, State

from .config import BAD_CHANNELS_ID, BROWSER_DATA_ID, BROWSER_GRAPH_ID, CHANNEL_SLIDER_ID


def register_callbacks(app):
    """Attach all browser callbacks to a Dash app."""
    app.clientside_callback(
        ClientsideFunction(namespace="mneJsBrowser", function_name="toggleBadChannel"),
        Output(BAD_CHANNELS_ID, "data"),
        Input(BROWSER_GRAPH_ID, "clickData"),
        State(BROWSER_GRAPH_ID, "figure"),
        State(BAD_CHANNELS_ID, "data"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        ClientsideFunction(namespace="mneJsBrowser", function_name="updateFigureWindow"),
        Output(BROWSER_GRAPH_ID, "figure"),
        Input(CHANNEL_SLIDER_ID, "value"),
        Input(BAD_CHANNELS_ID, "data"),
        State(BROWSER_GRAPH_ID, "figure"),
        State(BROWSER_DATA_ID, "data"),
    )
