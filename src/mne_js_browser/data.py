"""Data preparation utilities for the browser package."""

from __future__ import annotations

import mne
import numpy as np

from ._types import BrowserData
from .config import DEFAULT_N_CHANNELS, VISUAL_SCALE


def _annotation_overlays(raw: mne.io.BaseRaw) -> tuple[list[dict], list[dict]]:
    """Build static Plotly shapes and annotation labels."""
    shapes: list[dict] = []
    annotations: list[dict] = []

    for annot in raw.annotations:
        start = float(annot["onset"] - raw.first_samp / raw.info["sfreq"])
        end = start + float(annot["duration"])

        shapes.append(
            {
                "type": "rect",
                "xref": "x",
                "yref": "paper",
                "x0": start,
                "x1": end,
                "y0": 0,
                "y1": 1,
                "fillcolor": "red",
                "opacity": 0.5,
                "layer": "below",
                "line_width": 0,
            }
        )

        annotations.append(
            {
                "x": (start + end) / 2,
                "y": 1.0,
                "yref": "paper",
                "xref": "x",
                "text": annot["description"],
                "showarrow": False,
                "yshift": 10,
                "font": {"color": "black", "size": 10},
            }
        )

    return shapes, annotations


def prepare_browser_data(
    raw: mne.io.BaseRaw,
    *,
    picks: str | list[str] | list[int] | np.ndarray | None = "eeg",
    n_channels: int = DEFAULT_N_CHANNELS,
) -> BrowserData:
    """Convert an MNE Raw object to browser-ready data state."""
    picked_raw = raw.copy().pick(picks)

    all_data = picked_raw.get_data()
    all_data_scaled = all_data * VISUAL_SCALE
    times = picked_raw.times.copy()
    ch_names = list(picked_raw.ch_names)

    bads = [ch for ch in raw.info["bads"] if ch in ch_names]
    static_shapes, static_annotations = _annotation_overlays(raw)

    return BrowserData(
        times=times,
        all_data=all_data,
        all_data_scaled=all_data_scaled,
        ch_names=ch_names,
        bads=bads,
        n_channels=int(n_channels),
        full_tmin=float(times[0]),
        full_tmax=float(times[-1]),
        static_shapes=static_shapes,
        static_annotations=static_annotations,
    )


def to_client_dict(data: BrowserData) -> dict:
    """Serialize BrowserData to JSON-safe structures for Dash stores."""
    return {
        "times": data.times.tolist(),
        "all_data": data.all_data.tolist(),
        "all_data_scaled": data.all_data_scaled.tolist(),
        "ch_names": data.ch_names,
        "bads": data.bads,
        "n_channels": data.n_channels,
        "full_tmin": data.full_tmin,
        "full_tmax": data.full_tmax,
        "static_shapes": data.static_shapes,
        "static_annotations": data.static_annotations,
    }
