"""Turning raw export rows into arrival/activation timestamps and delays.

The export of the editorial system contains, per image, the activation
timestamp (date and time) and an IPTC instruction field whose text starts
with the arrival time of day in square brackets, e.g.
``[23:51:45] *** World Rights ***``. The arrival timestamp is reconstructed by
combining the activation date with that time of day.

Midnight crossing: an image that arrives at 23:58 and is activated at 00:03
carries the activation date of the next day. The arrival is therefore moved to
the previous day when the same-day combination lies more than
:data:`MIDNIGHT_SHIFT_THRESHOLD` after the activation. Smaller inversions
(arrival a few seconds or minutes after activation) are clock skew between the
systems; they stay on the same day, yield a negative delay and are dropped.
Version 1.x shifted every inversion to the previous day and thereby turned
clock skew into delays of almost 24 hours.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

log = logging.getLogger(__name__)

# Column names of the editorial export.
COL_IPTC_DE = "IPTC_DE Anweisung"
COL_IPTC_EN = "IPTC_EN Anweisung"
COL_UPLOAD = "Bild Upload Zeitpunkt"
COL_PUBLISHED = "Bild Veröffentlicht"
COL_ACTIVATION = "Bild Aktivierungszeitpunkt"
EXPECTED_COLUMNS = (COL_IPTC_DE, COL_IPTC_EN, COL_UPLOAD, COL_PUBLISHED, COL_ACTIVATION)

# Alternative export with precomputed timestamps.
COL_ARRIVAL = "Bildankunft"
COL_ONLINE = "Onlinestellung"
KNOWN_COLUMNS = frozenset((*EXPECTED_COLUMNS, COL_ARRIVAL, COL_ONLINE))

# Columns of the processed frame.
ARRIVAL = "arrival"
ACTIVATION = "activation"
DELAY = "delay_minutes"
SOURCE = "source_file"
TIME_FEATURES = ("year", "month", "day", "hour", "weekday", "iso_year", "iso_week")

DEFAULT_MAX_DELAY_MINUTES = 24 * 60
MIDNIGHT_SHIFT_THRESHOLD = pd.Timedelta(hours=12)
IPTC_TIME_PATTERN = r"\[(\d{2}):(\d{2}):(\d{2})\]"
EXPORT_TIMESTAMP_FORMAT = "%d.%m.%Y %H:%M:%S"


@dataclass(frozen=True)
class ProcessingReport:
    """Row counts of one :func:`process` run."""

    rows_in: int
    rows_out: int
    dropped_unparseable: int
    dropped_negative: int
    dropped_above_max: int

    @property
    def dropped(self) -> int:
        return self.dropped_unparseable + self.dropped_negative + self.dropped_above_max


def extract_iptc_time(series: pd.Series) -> pd.Series:
    """Extract the ``[HH:MM:SS]`` prefix of an IPTC instruction as a timedelta.

    Values without the prefix become ``NaT``.
    """
    parts = series.astype("string").str.extract(IPTC_TIME_PATTERN)
    numbers = parts.apply(pd.to_numeric, errors="coerce")
    seconds = numbers[0] * 3600 + numbers[1] * 60 + numbers[2]
    return pd.to_timedelta(seconds, unit="s")


def parse_timestamps(series: pd.Series) -> pd.Series:
    """Parse export timestamps (``dd.mm.yyyy HH:MM:SS``); other formats are tried too."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return series
    parsed = pd.to_datetime(series, format=EXPORT_TIMESTAMP_FORMAT, errors="coerce")
    unparsed = parsed.isna() & series.notna()
    if unparsed.any():
        parsed = parsed.copy()
        parsed[unparsed] = pd.to_datetime(
            series[unparsed], dayfirst=True, format="mixed", errors="coerce"
        )
    return parsed


def combine_arrival(activation: pd.Series, time_of_day: pd.Series) -> pd.Series:
    """Combine the activation date with the arrival time of day.

    If the combination lies more than :data:`MIDNIGHT_SHIFT_THRESHOLD` after
    the activation, the image arrived on the previous day.
    """
    arrival = activation.dt.normalize() + time_of_day
    previous_day = (arrival - activation) > MIDNIGHT_SHIFT_THRESHOLD
    return arrival.mask(previous_day, arrival - pd.Timedelta(days=1))


def _timestamps(frame: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    columns = set(frame.columns)
    if COL_IPTC_DE in columns and COL_ACTIVATION in columns:
        activation = parse_timestamps(frame[COL_ACTIVATION])
        arrival = combine_arrival(activation, extract_iptc_time(frame[COL_IPTC_DE]))
        return arrival, activation
    if COL_ARRIVAL in columns and (COL_ONLINE in columns or COL_ACTIVATION in columns):
        online_column = COL_ONLINE if COL_ONLINE in columns else COL_ACTIVATION
        return parse_timestamps(frame[COL_ARRIVAL]), parse_timestamps(frame[online_column])
    raise ValueError(
        "could not identify the required columns; expected "
        f"{COL_IPTC_DE!r} and {COL_ACTIVATION!r} (or {COL_ARRIVAL!r} and {COL_ONLINE!r}), "
        f"found {sorted(columns)}"
    )


def add_time_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add calendar columns derived from the arrival timestamp."""
    arrival = frame[ARRIVAL]
    iso = arrival.dt.isocalendar()
    return frame.assign(
        year=arrival.dt.year,
        month=arrival.dt.month,
        day=arrival.dt.day,
        hour=arrival.dt.hour,
        weekday=arrival.dt.weekday,
        iso_year=iso["year"].astype(int),
        iso_week=iso["week"].astype(int),
    )


def process(
    frame: pd.DataFrame, max_delay_minutes: float = DEFAULT_MAX_DELAY_MINUTES
) -> tuple[pd.DataFrame, ProcessingReport]:
    """Compute arrival, activation and delay for every usable row.

    Rows whose timestamps cannot be parsed, whose delay is negative or whose
    delay exceeds ``max_delay_minutes`` are dropped; the report says how many.
    """
    arrival, activation = _timestamps(frame)
    result = pd.DataFrame({ARRIVAL: arrival, ACTIVATION: activation})
    if SOURCE in frame.columns:
        result[SOURCE] = frame[SOURCE].to_numpy()
    result[DELAY] = (result[ACTIVATION] - result[ARRIVAL]).dt.total_seconds() / 60

    parseable = result[DELAY].notna()
    negative = parseable & (result[DELAY] < 0)
    above_max = parseable & (result[DELAY] > max_delay_minutes)
    keep = parseable & ~negative & ~above_max

    report = ProcessingReport(
        rows_in=len(frame),
        rows_out=int(keep.sum()),
        dropped_unparseable=int((~parseable).sum()),
        dropped_negative=int(negative.sum()),
        dropped_above_max=int(above_max.sum()),
    )
    if report.rows_in and report.dropped_unparseable / report.rows_in > 0.05:
        log.warning(
            "%d of %d rows (%.0f %%) have no usable timestamps, e.g. no [HH:MM:SS] prefix in %r",
            report.dropped_unparseable,
            report.rows_in,
            100 * report.dropped_unparseable / report.rows_in,
            COL_IPTC_DE,
        )
    if report.dropped:
        log.info(
            "dropped %d of %d rows (%d unparseable, %d negative, %d above %.0f min)",
            report.dropped,
            report.rows_in,
            report.dropped_unparseable,
            report.dropped_negative,
            report.dropped_above_max,
            max_delay_minutes,
        )
    result = result[keep].reset_index(drop=True)
    return add_time_features(result), report
