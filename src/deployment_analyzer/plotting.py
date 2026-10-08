"""Heatmap figures built without ``pyplot`` so they are safe to use in a GUI."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from .analysis import Granularity

DEFAULT_CMAP = "RdYlGn_r"
DEFAULT_TITLE = "Deployment delays"
MAX_ROW_LABELS = 40


def figure_size(rows: int, columns: int, granularity: Granularity) -> tuple[float, float]:
    """Figure size in inches; cells are square except for timeline views (2:1)."""
    if granularity in ("weekly", "monthly"):
        standard_rows = 7 if granularity == "weekly" else 12
        return 16.0, max(4.0, min(standard_rows * 0.6, 10.0))
    if granularity == "hourly":
        return 16.0, 3.0
    width = 16.0
    height = max(4.0, min(width * rows / max(columns, 1) * 0.35, 18.0))
    return width, height


def color_limits(
    values: np.ndarray, granularity: Granularity
) -> tuple[float, float] | tuple[None, None]:
    """Robust colour limits so that single outliers do not flatten the map."""
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return None, None
    low, high = (10, 95) if granularity in ("daily", "yearly") else (5, 95)
    vmin, vmax = np.percentile(finite, [low, high])
    if vmin == vmax:
        vmin, vmax = (0.0, 1.0) if vmax == 0 else (vmin * 0.9, vmax * 1.1)
    return float(vmin), float(vmax)


def heatmap_figure(
    pivot: pd.DataFrame,
    granularity: Granularity,
    title: str = DEFAULT_TITLE,
    subtitle: str | None = None,
    cmap: str = DEFAULT_CMAP,
) -> Figure:
    """Render a pivot table from :func:`~deployment_analyzer.analysis.pivot_delays`."""
    rows, columns = pivot.shape
    # Constrained layout is recomputed on every resize, e.g. inside the GUI canvas.
    fig = Figure(figsize=figure_size(rows, columns, granularity), layout="constrained")
    ax = fig.add_subplot(111)

    if pivot.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=14)
        ax.set_axis_off()
        return fig

    colormap = matplotlib.colormaps[cmap].with_extremes(bad="white")
    values = pivot.to_numpy(dtype=float)
    vmin, vmax = color_limits(values, granularity)
    timeline = granularity in ("daily", "yearly")

    sns.heatmap(
        pivot,
        ax=ax,
        cmap=colormap,
        mask=np.isnan(values),
        vmin=vmin,
        vmax=vmax,
        linewidths=0 if timeline and rows > 31 else 0.5,
        linecolor="white",
        square=not timeline,
        cbar_kws={"label": "Average delay (minutes)"},
    )
    ax.set_xlabel("Hour of arrival")
    ax.set_ylabel("")
    ax.tick_params(axis="x", labelsize=8, rotation=0)

    if rows > MAX_ROW_LABELS:
        step = int(np.ceil(rows / MAX_ROW_LABELS))
        positions = np.arange(0, rows, step) + 0.5
        ax.set_yticks(positions)
        ax.set_yticklabels(pivot.index[::step], fontsize=7, rotation=0)
    else:
        ax.tick_params(axis="y", labelsize=8, rotation=0)

    ax.set_title(f"{title}\n{subtitle}" if subtitle else title, fontsize=13, pad=10)
    return fig


def save_figure(fig: Figure, path: str | Path, dpi: int = 200) -> Path:
    """Save a figure; the format follows the file extension (png, pdf, svg, ...)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", dpi=dpi)
    return path
