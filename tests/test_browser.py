import dash

from mne_js_browser import RawBrowser, create_browser_app


def test_create_browser_app_builds_dash_app(toy_raw):
    app = create_browser_app(toy_raw, picks="eeg", n_channels=3)

    assert isinstance(app, dash.Dash)
    assert app.layout is not None


def test_raw_browser_wraps_app(toy_raw):
    browser = RawBrowser(toy_raw, picks="eeg", n_channels=2, show=False)

    assert isinstance(browser.app, dash.Dash)
