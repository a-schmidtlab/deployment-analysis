"""Command-line interface: batch analysis or launching the GUI."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .analysis import (
    GRANULARITIES,
    filter_iso_week,
    filter_month,
    filter_year,
    pivot_delays,
    statistics,
)
from .loading import LoadError, load_files
from .plotting import DEFAULT_CMAP, heatmap_figure, save_figure
from .processing import DEFAULT_MAX_DELAY_MINUTES, process

log = logging.getLogger(__name__)

STATISTIC_LABELS = (
    ("total_records", "Records", "{:,.0f}"),
    ("avg_delay", "Average delay", "{:.1f} min"),
    ("median_delay", "Median delay", "{:.1f} min"),
    ("p95_delay", "95th percentile", "{:.1f} min"),
    ("min_delay", "Minimum delay", "{:.1f} min"),
    ("max_delay", "Maximum delay", "{:.1f} min"),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deployment-analyzer",
        description=(
            "Analyze image deployment delays from editorial system exports. "
            "Without input files (or with --gui) the graphical interface starts."
        ),
    )
    parser.add_argument("files", nargs="*", type=Path, help="CSV or Excel export files")
    parser.add_argument("--gui", action="store_true", help="start the GUI (files are preloaded)")
    parser.add_argument("-o", "--output", type=Path, help="write the heatmap to this image file")
    parser.add_argument(
        "-g",
        "--granularity",
        choices=GRANULARITIES,
        default="daily",
        help="row period of the heatmap (default: %(default)s)",
    )
    parser.add_argument(
        "--year", type=int, help="restrict to a calendar year (ISO year with --week)"
    )
    parser.add_argument(
        "--month", type=int, choices=range(1, 13), metavar="1-12", help="restrict to a month"
    )
    parser.add_argument(
        "--week", type=int, choices=range(1, 54), metavar="1-53", help="restrict to an ISO week"
    )
    parser.add_argument(
        "--max-delay",
        type=float,
        default=DEFAULT_MAX_DELAY_MINUTES,
        metavar="MINUTES",
        help="drop rows with a larger delay (default: %(default)s)",
    )
    parser.add_argument("--export-csv", type=Path, metavar="FILE", help="write the processed rows")
    parser.add_argument(
        "--cmap", default=DEFAULT_CMAP, help="matplotlib colormap (default: %(default)s)"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    # Used by the release build to check that Tk and the GUI are bundled.
    parser.add_argument("--self-test", action="store_true", help=argparse.SUPPRESS)
    return parser


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handlers: list[logging.Handler] = []
    if sys.stderr is not None:  # None in windowed (frozen) builds
        handlers.append(logging.StreamHandler(sys.stderr))
    if getattr(sys, "frozen", False):
        # Frozen builds may run without a console; keep a log next to the executable.
        from logging.handlers import RotatingFileHandler

        log_dir = Path(sys.executable).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                log_dir / "deployment_analyzer.log", maxBytes=2_000_000, backupCount=2
            )
        )
    logging.basicConfig(
        level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s", handlers=handlers
    )


def select_period(frame, year: int | None, month: int | None, week: int | None):
    if week is not None:
        if year is None:
            raise ValueError("--week requires --year (the ISO year)")
        return filter_iso_week(frame, year, week)
    if month is not None:
        if year is None:
            raise ValueError("--month requires --year")
        return filter_month(frame, year, month)
    if year is not None:
        return filter_year(frame, year)
    return frame


def describe_period(year: int | None, month: int | None, week: int | None) -> str | None:
    if week is not None:
        return f"ISO week {week}, {year}"
    if month is not None:
        return f"{year}-{month:02d}"
    if year is not None:
        return str(year)
    return None


def format_statistics(stats: dict[str, float]) -> str:
    width = max(len(label) for _, label, _ in STATISTIC_LABELS)
    return "\n".join(
        f"{label:<{width}}  {template.format(stats[key])}"
        for key, label, template in STATISTIC_LABELS
    )


def run_batch(args: argparse.Namespace) -> int:
    raw = load_files(args.files)
    data, report = process(raw, args.max_delay)
    print(
        f"Loaded {report.rows_in:,} rows from {len(args.files)} file(s); "
        f"{report.rows_out:,} usable, {report.dropped:,} dropped "
        f"({report.dropped_unparseable} unparseable, {report.dropped_negative} negative, "
        f"{report.dropped_above_max} above {args.max_delay:.0f} min)"
    )
    subset = select_period(data, args.year, args.month, args.week)
    period = describe_period(args.year, args.month, args.week)
    if subset.empty:
        print(f"No data for {period}", file=sys.stderr)
        return 1
    if period:
        print(f"Period: {period}")
    print(format_statistics(statistics(subset)))

    if args.export_csv:
        args.export_csv.parent.mkdir(parents=True, exist_ok=True)
        subset.to_csv(args.export_csv, index=False)
        print(f"Processed rows written to {args.export_csv}")
    if args.output:
        pivot = pivot_delays(subset, args.granularity)
        subtitle = f"{args.granularity} view" + (f", {period}" if period else "")
        fig = heatmap_figure(pivot, args.granularity, subtitle=subtitle, cmap=args.cmap)
        save_figure(fig, args.output)
        print(f"Heatmap written to {args.output}")
    return 0


def self_test() -> int:
    """Import the GUI, open and close a hidden window; 0 on success."""
    try:
        import tkinter as tk

        from .gui import AnalyzerApp

        root = tk.Tk()
        root.withdraw()
        AnalyzerApp(root)
        root.update()
        root.destroy()
    except Exception:
        log.exception("self-test failed")
        return 1
    log.info("self-test passed")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configure_logging(args.verbose)
    if args.self_test:
        return self_test()
    if args.gui or not args.files:
        from .gui import run_gui

        return run_gui(args.files, max_delay_minutes=args.max_delay)
    try:
        return run_batch(args)
    except (LoadError, ValueError) as exc:
        log.debug("batch run failed", exc_info=True)
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
