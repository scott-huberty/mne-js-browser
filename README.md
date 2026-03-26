# mne-js-browser

Interactive browser app for prepared `mne.io.Raw` data.

## Quick start

```python
from mne_js_browser import RawBrowser

browser = RawBrowser(raw, picks="eeg", n_channels=20)
browser.run()
```

Or construct the Dash app directly:

```python
from mne_js_browser import create_browser_app

app = create_browser_app(raw, picks="eeg", n_channels=20)
app.run()
```

For demo-data loading, see `examples/plot_raw_browser.py`.
