import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure

from deployment_analyzer.analysis import GRANULARITIES, pivot_delays
from deployment_analyzer.plotting import color_limits, figure_size, heatmap_figure, save_figure
from deployment_analyzer.processing import process


@pytest.fixture(scope="module")
def data(export_frame):
    return process(export_frame)[0]


@pytest.mark.parametrize("granularity", GRANULARITIES)
def test_heatmap_figure(data, granularity, tmp_path):
    fig = heatmap_figure(pivot_delays(data, granularity), granularity, subtitle="test")
    assert isinstance(fig, Figure)
    assert fig.axes[0].get_title().startswith("Deployment delays")
    path = save_figure(fig, tmp_path / granularity / "heatmap.png")
    assert path.is_file() and path.stat().st_size > 1000


def test_heatmap_figure_empty():
    fig = heatmap_figure(pd.DataFrame(), "daily")
    assert fig.axes[0].texts[0].get_text() == "No data"


def test_heatmap_many_rows_thins_labels():
    index = pd.date_range("2025-01-01", periods=200, freq="D").strftime("%Y-%m-%d")
    pivot = pd.DataFrame(np.random.default_rng(0).random((200, 24)), index=index, columns=range(24))
    fig = heatmap_figure(pivot, "yearly")
    assert len(fig.axes[0].get_yticklabels()) < 60


def test_color_limits():
    assert color_limits(np.array([np.nan, np.nan]), "daily") == (None, None)
    assert color_limits(np.array([3.0, 3.0, np.nan]), "daily") == pytest.approx((2.7, 3.3))
    assert color_limits(np.zeros(5), "weekly") == (0.0, 1.0)
    vmin, vmax = color_limits(np.arange(100, dtype=float), "weekly")
    assert vmin < vmax


def test_figure_size():
    assert figure_size(7, 24, "weekly")[1] < figure_size(12, 24, "monthly")[1]
    assert figure_size(365, 24, "yearly")[1] <= 18
    assert figure_size(1, 24, "hourly") == (16.0, 3.0)
