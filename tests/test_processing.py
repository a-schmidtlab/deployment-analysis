import numpy as np
import pandas as pd
import pytest
from conftest import export_from_pairs

from deployment_analyzer.processing import (
    ACTIVATION,
    ARRIVAL,
    COL_ACTIVATION,
    COL_ARRIVAL,
    COL_IPTC_DE,
    COL_ONLINE,
    DELAY,
    TIME_FEATURES,
    combine_arrival,
    extract_iptc_time,
    parse_timestamps,
    process,
)


def test_extract_iptc_time():
    series = pd.Series(["[23:51:45] *** World Rights ***", "no prefix", None, "[00:00:00] x"])
    result = extract_iptc_time(series)
    assert result.iloc[0] == pd.Timedelta(hours=23, minutes=51, seconds=45)
    assert pd.isna(result.iloc[1])
    assert pd.isna(result.iloc[2])
    assert result.iloc[3] == pd.Timedelta(0)


def test_parse_timestamps_export_format():
    series = pd.Series(["31.03.2024 23:55:07", "01.02.2025 00:00:01", "garbage", None])
    parsed = parse_timestamps(series)
    assert parsed.iloc[0] == pd.Timestamp("2024-03-31 23:55:07")
    assert parsed.iloc[1] == pd.Timestamp("2025-02-01 00:00:01")
    assert pd.isna(parsed.iloc[2])
    assert pd.isna(parsed.iloc[3])


def test_parse_timestamps_mixed_and_native():
    series = pd.Series(["2024-03-31 23:55:07", "31.03.2024 23:55:07"])
    parsed = parse_timestamps(series)
    assert (parsed == pd.Timestamp("2024-03-31 23:55:07")).all()
    native = pd.Series(pd.to_datetime(["2024-03-31 23:55:07"]))
    assert parse_timestamps(native).equals(native)


def test_combine_arrival_midnight_crossing():
    activation = pd.Series(
        pd.to_datetime(["2024-03-31 23:55:07", "2024-04-01 00:03:00", "2024-04-01 12:00:00"])
    )
    time_of_day = pd.Series(pd.to_timedelta(["23:51:45", "23:58:00", "11:30:00"]))
    arrival = combine_arrival(activation, time_of_day)
    assert arrival.iloc[0] == pd.Timestamp("2024-03-31 23:51:45")
    assert arrival.iloc[1] == pd.Timestamp("2024-03-31 23:58:00"), (
        "arrival before midnight, activation after"
    )
    assert arrival.iloc[2] == pd.Timestamp("2024-04-01 11:30:00")


def test_process_roundtrip(export_frame, timestamps):
    data, report = process(export_frame)
    assert report.rows_in == len(export_frame)
    assert report.dropped == 0
    assert set(TIME_FEATURES) <= set(data.columns)
    expected = timestamps.sort_values("activation", ascending=False).reset_index(drop=True)
    pd.testing.assert_series_equal(data[ARRIVAL], expected["arrival"], check_names=False)
    pd.testing.assert_series_equal(data[ACTIVATION], expected["activation"], check_names=False)
    expected_delay = (expected["activation"] - expected["arrival"]).dt.total_seconds() / 60
    np.testing.assert_allclose(data[DELAY], expected_delay)
    assert (data["weekday"] == data[ARRIVAL].dt.weekday).all()


def test_process_drops_invalid_rows():
    frame = pd.DataFrame(
        {
            COL_ARRIVAL: [
                "03.02.2025 10:00:00",  # fine
                "03.02.2025 10:10:00",  # negative: activation before arrival
                "03.02.2025 10:00:00",  # 25 h: above maximum
                "not a date",  # unparseable
            ],
            COL_ONLINE: [
                "03.02.2025 10:05:00",
                "03.02.2025 10:05:00",
                "04.02.2025 11:00:00",
                "03.02.2025 10:00:00",
            ],
        }
    )
    data, report = process(frame)
    assert len(data) == 1
    assert data[DELAY].iloc[0] == pytest.approx(5.0)
    assert (report.dropped_negative, report.dropped_above_max, report.dropped_unparseable) == (
        1,
        1,
        1,
    )
    assert report.rows_out == 1 and report.rows_in == 4


def test_process_export_rows_without_iptc_time_are_dropped():
    frame = export_from_pairs([("2025-02-03 10:00:00", "2025-02-03 10:05:00")])
    frame.loc[1] = ["no time", "no time", "03.02.2025 10:00:00", "Ja", "03.02.2025 10:00:00"]
    data, report = process(frame)
    assert len(data) == 1
    assert report.dropped_unparseable == 1


def test_process_clock_skew_is_not_a_midnight_crossing():
    """Arrival time of day slightly after activation is clock skew, not 'previous day'.

    Version 1.x turned such rows into delays of almost 24 hours.
    """
    frame = export_from_pairs(
        [
            ("2025-02-03 10:00:20", "2025-02-03 10:00:00"),  # 20 s skew
            ("2025-02-03 13:00:00", "2025-02-03 10:00:00"),  # 3 h inversion
            ("2025-02-02 23:58:00", "2025-02-03 00:03:00"),  # real midnight crossing
        ]
    )
    data, report = process(frame)
    assert report.dropped_negative == 2
    assert len(data) == 1
    assert data[ARRIVAL].iloc[0] == pd.Timestamp("2025-02-02 23:58:00")
    assert data[DELAY].iloc[0] == pytest.approx(5.0)


def test_combine_arrival_threshold():
    activation = pd.Series(pd.to_datetime(["2025-02-03 11:00:00", "2025-02-03 11:00:00"]))
    time_of_day = pd.Series(pd.to_timedelta(["23:00:00", "23:00:01"]))
    arrival = combine_arrival(activation, time_of_day)
    assert arrival.iloc[0] == pd.Timestamp("2025-02-03 23:00:00"), "exactly 12 h: same day"
    assert arrival.iloc[1] == pd.Timestamp("2025-02-02 23:00:01"), "more than 12 h: previous day"


def test_process_max_delay_parameter():
    frame = export_from_pairs([("2025-02-03 10:00:00", "2025-02-03 10:30:00")])
    assert len(process(frame, max_delay_minutes=20)[0]) == 0
    assert len(process(frame, max_delay_minutes=30)[0]) == 1


def test_process_iso_week_at_year_boundary():
    frame = export_from_pairs([("2024-12-30 10:00:00", "2024-12-30 10:05:00")])
    data, _ = process(frame)
    assert data["year"].iloc[0] == 2024
    assert (data["iso_year"].iloc[0], data["iso_week"].iloc[0]) == (2025, 1)


def test_process_alternative_columns():
    frame = pd.DataFrame(
        {COL_ARRIVAL: ["03.02.2025 10:00:00"], COL_ONLINE: ["03.02.2025 10:07:30"]}
    )
    data, _ = process(frame)
    assert data[DELAY].iloc[0] == pytest.approx(7.5)


def test_process_unknown_columns():
    with pytest.raises(ValueError, match="required columns"):
        process(pd.DataFrame({"a": [1], "b": [2]}))


def test_process_native_datetimes_from_excel():
    frame = pd.DataFrame(
        {
            COL_IPTC_DE: ["[09:58:00] *** World Rights ***"],
            COL_ACTIVATION: pd.to_datetime(["2025-02-03 10:00:00"]),
        }
    )
    data, _ = process(frame)
    assert data[DELAY].iloc[0] == pytest.approx(2.0)
