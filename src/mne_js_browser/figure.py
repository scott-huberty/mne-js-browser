"""Pure Plotly figure construction."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from ._types import BrowserData
from .config import APP_HEIGHT, APP_WIDTH


def make_base_figure(
    data: BrowserData,
    *,
    channel_start: int = 0,
    x_range: tuple[float, float] = (0.0, 10.0),
) -> go.Figure:
    """Create the browser figure with fixed number of traces."""
    n_channels = data.n_channels
    x0, x1 = x_range
    x0 = max(data.full_tmin, float(x0))
    x1 = min(data.full_tmax, float(x1))

    start = max(0, min(channel_start, max(0, len(data.ch_names) - n_channels)))

    traces: list[go.Scattergl] = []
    ticktext: list[str] = []

    for ii in range(n_channels):
        ch_idx = start + ii
        if ch_idx < len(data.ch_names):
            ch_name = data.ch_names[ch_idx]
            y = data.all_data_scaled[ch_idx] + ii
            amplitude = data.all_data[ch_idx]
            color = "red" if ch_name in data.bads else "black"
            ticktext.append(ch_name)
        else:
            ch_name = ""
            y = np.full(data.times.shape, np.nan)
            amplitude = np.full(data.times.shape, np.nan)
            color = "black"
            ticktext.append("")

        traces.append(
            go.Scattergl(
                x=data.times,
                y=y,
                name=ch_name,
                mode="lines",
                text=amplitude,
                line={"color": color, "width": 1},
                showlegend=False,
                hovertemplate=(
                    f"<b>Channel:</b> {ch_name}<br>"
                    "<b>Time:</b> %{x:.2f} s<br>"
                    "<b>Amplitude:</b> %{text:.7f} V<br>"
                    "<extra></extra>"
                ),
            )
        )

    fig = go.Figure(data=traces)
    fig.update_layout(
        showlegend=False,
        autosize=False,
        width=APP_WIDTH,
        height=APP_HEIGHT,
        margin={"l": 20, "r": 20, "b": 20, "t": 20},
        xaxis={
            "title": "Time (s)",
            "fixedrange": True,
            "ticks": "outside",
            "side": "bottom",
            "rangeslider": {
                "visible": True,
                "thickness": 0.01,
                "bgcolor": "LightGrey",
            },
            "type": "linear",
            "range": [x0, x1],
            "minallowed": data.full_tmin,
            "maxallowed": data.full_tmax,
        },
        yaxis={
            "zeroline": False,
            "showgrid": False,
            "range": [-0.5, n_channels - 0.5],
            "tickvals": list(range(n_channels)),
            "ticktext": ticktext,
        },
        shapes=data.static_shapes,
        annotations=data.static_annotations,
        uirevision="browser",
    )
    return fig
