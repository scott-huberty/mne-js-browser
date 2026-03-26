import mne
import numpy as np
import pytest


@pytest.fixture
def toy_raw():
    rng = np.random.default_rng(42)
    sfreq = 100.0
    ch_names = ["EEG 001", "EEG 002", "EEG 003", "EEG 004"]
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types="eeg")
    data = rng.standard_normal((4, 300)) * 1e-6

    raw = mne.io.RawArray(data, info)
    raw.info["bads"] = ["EEG 002"]
    raw.set_annotations(mne.Annotations(onset=[0.5], duration=[0.2], description=["BAD_blink"]))
    return raw
