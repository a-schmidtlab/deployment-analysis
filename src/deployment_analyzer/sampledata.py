"""Synthetic export data in the format of the editorial system.

Used by the test suite and by ``tools/make_sample_data.py``. The numbers are
made up; no real operational data is contained in this repository.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .processing import (
    COL_ACTIVATION,
    COL_IPTC_DE,
    COL_IPTC_EN,
    COL_PUBLISHED,
    COL_UPLOAD,
    EXPECTED_COLUMNS,
    EXPORT_TIMESTAMP_FORMAT,
)

RIGHTS_TEXTS = (
    "*** World Rights ***",
    "World Rights Except UK and Ireland * GBROUT IRLOUT",
    "*** Germany only ***",
)

# Relative arrival volume and additional delay per hour of day.
HOUR_WEIGHTS = np.array(
    [1, 1, 1, 1, 1, 2, 4, 7, 9, 10, 10, 9, 8, 9, 10, 10, 9, 8, 7, 6, 5, 4, 3, 2]
)
HOUR_EXTRA_DELAY = np.array(
    [0, 0, 0, 0, 0, 0, 0, 1, 3, 6, 5, 2, 1, 1, 2, 4, 6, 7, 5, 2, 1, 0, 0, 0]
)


def generate_timestamps(
    n: int = 2000, start: str = "2025-02-03", days: int = 21, seed: int = 7
) -> pd.DataFrame:
    """Arrival and activation timestamps with a plausible daily pattern."""
    rng = np.random.default_rng(seed)
    start_ts = pd.Timestamp(start)
    day = rng.integers(0, days, size=n)
    hour = rng.choice(24, size=n, p=HOUR_WEIGHTS / HOUR_WEIGHTS.sum())
    second = rng.integers(0, 3600, size=n)
    arrival = start_ts + pd.to_timedelta(day * 86400 + hour * 3600 + second, unit="s")
    delay = rng.gamma(shape=2.0, scale=1.5, size=n) + HOUR_EXTRA_DELAY[hour]
    outliers = rng.random(n) < 0.01
    delay = np.where(outliers, delay + rng.uniform(60, 240, size=n), delay)
    activation = arrival + pd.to_timedelta(np.round(delay * 60), unit="s")
    return pd.DataFrame({"arrival": arrival, "activation": activation})


def to_export_rows(timestamps: pd.DataFrame, seed: int = 7) -> pd.DataFrame:
    """Format arrival/activation pairs as rows of the editorial export."""
    rng = np.random.default_rng(seed)
    rights = rng.choice(RIGHTS_TEXTS, size=len(timestamps), p=(0.8, 0.15, 0.05))
    iptc = [
        f"[{arrival:%H:%M:%S}] {text}"
        for arrival, text in zip(timestamps["arrival"], rights, strict=True)
    ]
    activation = timestamps["activation"].dt.strftime(EXPORT_TIMESTAMP_FORMAT)
    frame = pd.DataFrame(
        {
            COL_IPTC_DE: iptc,
            COL_IPTC_EN: iptc,
            COL_UPLOAD: activation,
            COL_PUBLISHED: "Ja",
            COL_ACTIVATION: activation,
        }
    )
    return frame[list(EXPECTED_COLUMNS)]


def generate_export(
    n: int = 2000, start: str = "2025-02-03", days: int = 21, seed: int = 7
) -> pd.DataFrame:
    """Synthetic export rows, newest first like the real export."""
    timestamps = generate_timestamps(n, start, days, seed)
    timestamps = timestamps.sort_values("activation", ascending=False).reset_index(drop=True)
    return to_export_rows(timestamps, seed)
