"""Example: launch a browser app for MNE sample data."""

import mne

from mne_js_browser import RawBrowser


def main():
    data_path = mne.datasets.sample.data_path()
    raw_fname = data_path / "MEG" / "sample" / "sample_audvis_filt-0-40_raw.fif"

    raw = mne.io.Raw(raw_fname, preload=True).resample(100)
    raw.info["bads"] += ["EEG 005"]
    raw.set_annotations(
        mne.Annotations(
            onset=[0, 14],
            duration=[1, 1],
            description=["BAD_blink", "BAD_blink"],
        )
    )

    RawBrowser(raw)


if __name__ == "__main__":
    main()
