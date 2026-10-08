"""Period selection, pivot tables and summary statistics of processed data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import pandas as pd

from .processing import ARRIVAL, DELAY

Granularity = Literal["hourly", "daily", "weekly", "monthly", "yearly"]
GRANULARITIES: tuple[Granularity, ...] = ("hourly", "daily", "weekly", "monthly", "yearly")

HOURS = list(range(24))
WEEKDAY_LABELS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTH_LABELS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
STATISTIC_KEYS = (
    "total_records",
    "avg_delay",
    "median_delay",
    "min_delay",
    "max_delay",
    "p95_delay",
)


def filter_year(frame: pd.DataFrame, year: int) -> pd.DataFrame:
    return frame[frame["year"] == year]


def filter_month(frame: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
    return frame[(frame["year"] == year) & (frame["month"] == month)]


def filter_iso_week(frame: pd.DataFrame, iso_year: int, iso_week: int) -> pd.DataFrame:
    """Select one ISO week. Note that ISO year and calendar year differ around New Year."""
    return frame[(frame["iso_year"] == iso_year) & (frame["iso_week"] == iso_week)]


@dataclass
class Periods:
    """Calendar periods that contain data, for building navigation controls."""

    years: list[int] = field(default_factory=list)
    months: dict[int, list[int]] = field(default_factory=dict)
    weeks: dict[int, list[tuple[int, int]]] = field(default_factory=dict)
    """Per calendar year the ``(iso_year, iso_week)`` pairs that occur in it."""


def available_periods(frame: pd.DataFrame) -> Periods:
    periods = Periods()
    if frame.empty:
        return periods
    periods.years = sorted(int(year) for year in frame["year"].unique())
    for year in periods.years:
        rows = frame[frame["year"] == year]
        periods.months[year] = sorted(int(month) for month in rows["month"].unique())
        pairs = set(zip(rows["iso_year"].astype(int), rows["iso_week"].astype(int), strict=True))
        periods.weeks[year] = sorted(pairs)
    return periods


def _daily_labels(dates: pd.DatetimeIndex) -> list[str]:
    return [f"{WEEKDAY_LABELS[date.weekday()]} {date:%d.%m.}" for date in dates]


def pivot_delays(frame: pd.DataFrame, granularity: Granularity) -> pd.DataFrame:
    """Average delay per row period and hour of arrival (columns 0..23).

    Missing combinations are ``NaN``. Row periods by granularity:

    - ``hourly``: a single row over all data
    - ``daily``: one row per calendar date, labelled ``Mon 03.02.``
    - ``weekly``: Monday to Sunday (weekday profile)
    - ``monthly``: January to December (month profile)
    - ``yearly``: one row per calendar date, labelled ``2025-02-03``
    """
    if granularity not in GRANULARITIES:
        raise ValueError(f"unknown granularity {granularity!r}; choose from {GRANULARITIES}")
    if frame.empty:
        return pd.DataFrame(columns=HOURS, dtype=float)

    if granularity == "hourly":
        key, order, labels = pd.Series("All data", index=frame.index), ["All data"], ["All data"]
    elif granularity == "weekly":
        key, order, labels = frame["weekday"], list(range(7)), list(WEEKDAY_LABELS)
    elif granularity == "monthly":
        key, order, labels = frame["month"], list(range(1, 13)), list(MONTH_LABELS)
    else:
        key = frame[ARRIVAL].dt.normalize()
        dates = pd.date_range(key.min(), key.max(), freq="D")
        order = list(dates)
        labels = (
            _daily_labels(dates) if granularity == "daily" else list(dates.strftime("%Y-%m-%d"))
        )

    table = (
        frame.assign(_period=key)
        .pivot_table(values=DELAY, index="_period", columns="hour", aggfunc="mean")
        .reindex(index=order, columns=HOURS)
        .astype(float)
    )
    table.index = pd.Index(labels)
    table.index.name = None
    table.columns.name = None
    return table


def statistics(frame: pd.DataFrame) -> dict[str, float]:
    """Record count and delay summary (minutes) of a processed frame."""
    if frame.empty:
        return dict.fromkeys(STATISTIC_KEYS, 0.0) | {"total_records": 0}
    delay = frame[DELAY]
    return {
        "total_records": len(frame),
        "avg_delay": float(delay.mean()),
        "median_delay": float(delay.median()),
        "min_delay": float(delay.min()),
        "max_delay": float(delay.max()),
        "p95_delay": float(delay.quantile(0.95)),
    }
