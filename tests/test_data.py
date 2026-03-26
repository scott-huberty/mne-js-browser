import numpy as np

from mne_js_browser.data import prepare_browser_data, to_client_dict


def test_prepare_browser_data_and_serializer(toy_raw):
    data = prepare_browser_data(toy_raw, picks="eeg", n_channels=3)

    assert data.n_channels == 3
    assert data.all_data.shape[0] == 4
    assert data.all_data_scaled.shape == data.all_data.shape
    assert data.ch_names[1] == "EEG 002"
    assert "EEG 002" in data.bads
    assert np.isclose(data.full_tmin, 0.0)
    assert data.full_tmax > data.full_tmin
    assert len(data.static_shapes) == 1
    assert len(data.static_annotations) == 1

    payload = to_client_dict(data)
    assert payload["n_channels"] == 3
    assert payload["ch_names"] == data.ch_names
    assert isinstance(payload["times"], list)
    assert isinstance(payload["all_data"], list)
    assert isinstance(payload["all_data_scaled"], list)
