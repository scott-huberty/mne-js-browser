"""Shared type containers for browser data flow."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BrowserData:
    times: np.ndarray
    all_data: np.ndarray
    all_data_scaled: np.ndarray
    ch_names: list[str]
    bads: list[str]
    n_channels: int
    full_tmin: float
    full_tmax: float
    static_shapes: list[dict]
    static_annotations: list[dict]
