"""Deployment Analyzer: heatmaps of image deployment delays.

The package reads exports of an editorial image system, reconstructs the
arrival time of every image from the IPTC instruction field, computes the
delay until activation and aggregates the delays into hour-of-day heatmaps.
"""

from .analysis import (
    GRANULARITIES,
    Periods,
    available_periods,
    filter_iso_week,
    filter_month,
    filter_year,
    pivot_delays,
    statistics,
)
from .loading import LoadError, load_file, load_files
from .plotting import heatmap_figure, save_figure
from .processing import DEFAULT_MAX_DELAY_MINUTES, ProcessingReport, process

__version__ = "2.0.0"

__all__ = [
    "DEFAULT_MAX_DELAY_MINUTES",
    "GRANULARITIES",
    "LoadError",
    "Periods",
    "ProcessingReport",
    "__version__",
    "available_periods",
    "filter_iso_week",
    "filter_month",
    "filter_year",
    "heatmap_figure",
    "load_file",
    "load_files",
    "pivot_delays",
    "process",
    "save_figure",
    "statistics",
]
