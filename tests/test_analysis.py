import numpy as np
import pandas as pd
import pytest
from conftest import export_from_pairs

from deployment_analyzer.analysis import (
    GRANULARITIES,
    HOURS,
    MONTH_LABELS,
    WEEKDAY_LABELS,
    available_periods,
    filter_iso_week,
    filter_month,
    filter_year,
    pivot_delays,
    statistics,
)
from deployment_analyzer.processing import DELAY, process


@pytest.fixture(scope="module")
def data(export_frame):
    return process(export_frame)[0]


def test_filters(data):
    assert len(filter_year(data, 2025)) == len(data)
    assert filter_year(data, 2024).empty
    assert len(filter_month(data, 2025, 2)) == (data["month"] == 2).sum()
    week = filter_iso_week(data, 2025, 6)
    assert not week.empty
    assert (week["arrival"].dt.isocalendar().week == 6).all()


def test_available_periods(data):
    periods = available_periods(data)
    assert periods.years == [2025]
    assert periods.months[2025] == [2]
    assert periods.weeks[2025] == [(2025, 6), (2025, 7), (2025, 8)]
    assert available_periods(data.iloc[0:0]).years == []


def test_available_periods_year_boundary():
    frame = export_from_pairs([("2024-12-30 10:00:00", "2024-12-30 10:05:00")])
    periods = available_periods(process(frame)[0])
    assert periods.weeks[2024] == [(2025, 1)]


@pytest.mark.parametrize("granularity", GRANULARITIES)
def test_pivot_columns_are_hours(data, granularity):
    pivot = pivot_delays(data, granularity)
    assert list(pivot.columns) == HOURS
    assert pivot.dtypes.eq(float).all()


def test_pivot_shapes(data):
    assert list(pivot_delays(data, "weekly").index) == list(WEEKDAY_LABELS)
    assert list(pivot_delays(data, "monthly").index) == list(MONTH_LABELS)
    assert list(pivot_delays(data, "hourly").index) == ["All data"]
    assert len(pivot_delays(data, "yearly")) == 21
    assert pivot_delays(data, "yearly").index[0] == "2025-02-03"
    assert pivot_delays(data, "daily").index[0] == "Mon 03.02."


def test_pivot_values_are_means(data):
    pivot = pivot_delays(data, "weekly")
    monday_nine = data[(data["weekday"] == 0) & (data["hour"] == 9)][DELAY].mean()
    assert pivot.loc["Mon", 9] == pytest.approx(monday_nine)


def test_pivot_missing_cells_are_nan():
    frame = export_from_pairs(
        [
            ("2025-02-03 10:00:00", "2025-02-03 10:05:00"),
            ("2025-02-05 11:00:00", "2025-02-05 11:03:00"),
        ]
    )
    pivot = pivot_delays(process(frame)[0], "daily")
    assert list(pivot.index) == ["Mon 03.02.", "Tue 04.02.", "Wed 05.02."]
    assert pivot.loc["Mon 03.02.", 10] == pytest.approx(5.0)
    assert np.isnan(pivot.loc["Tue 04.02."]).all()
    assert np.isnan(pivot.loc["Mon 03.02.", 11])


def test_pivot_monthly_has_all_months(data):
    pivot = pivot_delays(data, "monthly")
    assert pivot.loc["Feb"].notna().any()
    assert pivot.drop(index="Feb").isna().all().all()


def test_pivot_empty_and_invalid(data):
    assert pivot_delays(data.iloc[0:0], "daily").empty
    with pytest.raises(ValueError, match="granularity"):
        pivot_delays(data, "decadal")


def test_statistics(data):
    stats = statistics(data)
    assert stats["total_records"] == len(data)
    assert stats["min_delay"] <= stats["median_delay"] <= stats["avg_delay"] <= stats["max_delay"]
    assert stats["p95_delay"] == pytest.approx(data[DELAY].quantile(0.95))
    empty = statistics(pd.DataFrame(columns=data.columns))
    assert empty["total_records"] == 0 and empty["avg_delay"] == 0.0
