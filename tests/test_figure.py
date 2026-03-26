from mne_js_browser.data import prepare_browser_data
from mne_js_browser.figure import make_base_figure


def test_make_base_figure_uses_fixed_channel_count(toy_raw):
    data = prepare_browser_data(toy_raw, picks="eeg", n_channels=3)
    fig = make_base_figure(data, channel_start=1, x_range=(0.0, 1.0))

    assert len(fig.data) == 3
    assert fig.layout.yaxis.ticktext[0] == "EEG 002"
    assert fig.layout.xaxis.range[0] == 0.0
    assert fig.layout.xaxis.range[1] <= data.full_tmax
