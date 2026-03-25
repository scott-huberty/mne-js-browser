import numpy as np
import mne
import plotly.graph_objects as go

import dash
from dash import dcc, html, Input, Output, Patch


data_path = mne.datasets.sample.data_path()
raw_fname = data_path / "MEG" / "sample" / "sample_audvis_filt-0-40_raw.fif"
assert raw_fname.exists()

raw = mne.io.Raw(raw_fname, preload=True).resample(100)
raw.info["bads"] += ["EEG 005"]
annots = mne.Annotations(
    onset=[0, 14],
    duration=[1, 1],
    description=["BAD_blink", "BAD_blink"],
)
raw.set_annotations(annots)

picks = mne.pick_types(raw.info, eeg=True, meg=False, exclude=[])

# -----------------------------------------------------------------------------
# Constants / precomputed data
# -----------------------------------------------------------------------------
N_CHANNELS = 20
FULL_TMIN = float(raw.times[0])
FULL_TMAX = float(raw.times[-1])
TIMES = raw.times.copy()

# Pre-extract all EEG data once so slider callbacks only slice numpy arrays.
# Shape: (n_eeg_channels, n_times)
ALL_DATA = raw.get_data(picks=picks)
ALL_DATA_SCALED = ALL_DATA * 1e4  # visual scaling for stacked display
# ALL_DATA_UV = ALL_DATA * 1e6  # for hover text

BADS = set(raw.info["bads"])
ALL_CH_NAMES = [raw.info["ch_names"][p] for p in picks]
MAX_SLIDER_VALUE = max(0, len(picks) - N_CHANNELS)


def _annotation_overlays():
    """Build static Plotly shapes/annotations once."""
    shapes = []
    annotations = []

    for annot in raw.annotations:
        start = float(annot["onset"] - raw.first_samp / raw.info["sfreq"])
        end = start + float(annot["duration"])

        shapes.append(
            dict(
                type="rect",
                xref="x",
                yref="paper",
                x0=start,
                x1=end,
                y0=0,
                y1=1,
                fillcolor="red",
                opacity=0.5,
                layer="below",
                line_width=0,
            )
        )

        # Put labels near the top of the plotting area in paper coords
        annotations.append(
            dict(
                x=(start + end) / 2,
                y=1.0,
                yref="paper",
                xref="x",
                text=annot["description"],
                showarrow=False,
                yshift=10,
                font=dict(color="black", size=10),
            )
        )

    return shapes, annotations


STATIC_SHAPES, STATIC_ANNOTATIONS = _annotation_overlays()


def _channel_window(channel_start, n_channels=N_CHANNELS):
    """Return channel names, colors, and stacked y arrays for one window."""
    ch_slice = slice(channel_start, channel_start + n_channels)
    ch_names = ALL_CH_NAMES[ch_slice]
    data = ALL_DATA_SCALED[ch_slice]

    y_arrays = []
    line_colors = []
    for ii, ch_name in enumerate(ch_names):
        y_arrays.append(data[ii] + ii)
        line_colors.append("red" if ch_name in BADS else "black")

    return ch_names, y_arrays, line_colors


def make_base_figure(channel_start=0, n_channels=N_CHANNELS, x_range=(0, 10)):
    """Create the figure once with static layout and exactly N_CHANNELS traces."""
    x0, x1 = x_range
    x0 = max(FULL_TMIN, float(x0))
    x1 = min(FULL_TMAX, float(x1))

    ch_names, y_arrays, line_colors = _channel_window(channel_start, n_channels)

    traces = []
    for ii in range(n_channels):
        if ii < len(ch_names):
            ch_name = ch_names[ii]
            y = y_arrays[ii]
            color = line_colors[ii]
        else:
            ch_name = ""
            y = np.full(TIMES.shape, np.nan)
            color = "black"

        traces.append(
            go.Scattergl(
                x=TIMES,
                y=y,
                name=ch_name,
                #text=np.round(ALL_DATA_UV[ii], 3),
                mode="lines",
                line=dict(color=color, width=1),
                showlegend=False,
                hovertemplate=(
                    f"<b>Channel:</b> {ch_name}<br>"
                    "<b>Time:</b> %{x:.2f} s<br>"
                   #"<b>Amplitude:</b> %{text:.2f} μV<br>"
                    "<extra></extra>"
                ),
            )
        )

    ticks = list(range(n_channels))
    ticktext = ch_names + [""] * (n_channels - len(ch_names))
    ymin, ymax = -0.5, n_channels - 0.5

    fig = go.Figure(data=traces)
    fig.update_layout(
        showlegend=False,
        autosize=False,
        width=900,
        height=540,
        margin=dict(l=20, r=20, b=20, t=20),
        xaxis=dict(
            title="Time (s)",
            fixedrange=True,
            ticks="outside",
            side="bottom",
            rangeslider=dict(
                visible=True,
                thickness=0.01,
                bgcolor="LightGrey",
            ),
            type="linear",
            range=[x0, x1],
            minallowed=FULL_TMIN,
            maxallowed=FULL_TMAX,
        ),
        yaxis=dict(
            zeroline=False,
            showgrid=False,
            range=[ymin, ymax],
            tickvals=ticks,
            ticktext=ticktext,
        ),
        shapes=STATIC_SHAPES,
        annotations=STATIC_ANNOTATIONS,
        # Helps Plotly preserve client-side UI state across server updates
        uirevision="browser",
    )
    return fig


# -----------------------------------------------------------------------------
# Dash app
# -----------------------------------------------------------------------------
app = dash.Dash(__name__)

app.layout = html.Div(
    style={"display": "flex", "alignItems": "flex-start", "columnGap": "8px"},
    children=[
        html.Div(
            children=[
                dcc.Slider(
                    id="channel-slider",
                    min=0,
                    max=MAX_SLIDER_VALUE,
                    step=1,
                    value=MAX_SLIDER_VALUE,
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
            children=[
                dcc.Graph(
                    id="browser",
                    figure=make_base_figure(channel_start=MAX_SLIDER_VALUE),
                )
            ],
            style={"flex": "1 1 auto", "minWidth": 0},
        ),
    ],
)


@app.callback(
    Output("browser", "figure"),
    Input("channel-slider", "value"),
)
def update_channels(slider_val):
    """
    Patch only the fields that actually change when channel scrolling:
    - trace y arrays
    - trace names
    - trace colors
    - y-axis tick labels
    """
    ch_names, y_arrays, line_colors = _channel_window(slider_val, N_CHANNELS)

    patch = Patch()

    # Update only the changing trace fields.
    for ii in range(N_CHANNELS):
        if ii < len(ch_names):
            ch_name = ch_names[ii]
            y = y_arrays[ii]
            color = line_colors[ii]
        else:
            ch_name = ""
            y = np.full(TIMES.shape, np.nan)
            color = "black"

        patch["data"][ii]["y"] = y
        patch["data"][ii]["name"] = ch_name
        patch["data"][ii]["line"]["color"] = color
        patch["data"][ii]["hovertemplate"] = (
            f"<b>Channel:</b> {ch_name}<br>"
            "<b>Time:</b> %{x:.2f} s<br>"
            # "<b>Amplitude:</b> %{text:.2f} μV<br>"
            "<extra></extra>"
        )

    # Update y-axis labels only.
    ticktext = ch_names + [""] * (N_CHANNELS - len(ch_names))
    patch["layout"]["yaxis"]["ticktext"] = ticktext

    return patch


if __name__ == "__main__":
    import webbrowser
    from threading import Timer

    Timer(1, lambda: webbrowser.open("http://127.0.0.1:8050/")).start()
    app.run()