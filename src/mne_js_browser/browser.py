"""Public orchestration layer for building and running the browser app."""

from __future__ import annotations

from pathlib import Path

from dash import Dash

from .callbacks import register_callbacks
from .config import DEFAULT_N_CHANNELS, DEFAULT_X_RANGE
from .data import prepare_browser_data, to_client_dict
from .figure import make_base_figure
from .layout import build_layout


def create_browser_app(
    raw,
    *,
    picks="eeg",
    n_channels: int = DEFAULT_N_CHANNELS,
    x_range: tuple[float, float] = DEFAULT_X_RANGE,
    **dash_kwargs,
):
    """Create a configured Dash app for browsing a prepared MNE Raw object."""
    if n_channels < 1:
        raise ValueError("n_channels must be >= 1")

    data = prepare_browser_data(raw, picks=picks, n_channels=n_channels)
    client_data = to_client_dict(data)

    max_slider_value = max(0, len(data.ch_names) - data.n_channels)
    slider_start = max_slider_value

    fig = make_base_figure(data, channel_start=slider_start, x_range=x_range)

    assets_folder = Path(__file__).resolve().parent / "assets"
    app = Dash(__name__, assets_folder=str(assets_folder), **dash_kwargs)
    app.layout = build_layout(
        initial_figure=fig,
        client_data=client_data,
        max_slider_value=max_slider_value,
        slider_start=slider_start,
    )

    register_callbacks(app)
    return app


class RawBrowser:
    """Simple wrapper around a Dash app with browser-centric defaults."""

    def __init__(
        self,
        raw,
        *,
        picks="eeg",
        n_channels: int = DEFAULT_N_CHANNELS,
        x_range: tuple[float, float] = DEFAULT_X_RANGE,
        **dash_kwargs,
    ):
        self.app = create_browser_app(
            raw,
            picks=picks,
            n_channels=n_channels,
            x_range=x_range,
            **dash_kwargs,
        )

    def run(self, *args, **kwargs):
        """Proxy to ``dash.Dash.run``."""
        return self.app.run(*args, **kwargs)


def main():
    raise RuntimeError(
        "No CLI demo is bundled in the package. Use examples/plot_raw_browser.py instead."
    )
