"""Tkinter GUI: import exports, navigate periods, show and export heatmaps.

Threading rule: only file loading and processing run in a worker thread. The
worker never touches Tk; it puts its result into a queue that the main thread
polls with ``root.after``. All pivoting, plotting and widget updates happen on
the Tk main thread.
"""

from __future__ import annotations

import logging
import queue
import threading
import tkinter as tk
import traceback
from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from . import __version__
from .analysis import (
    MONTH_LABELS,
    Granularity,
    Periods,
    available_periods,
    filter_iso_week,
    filter_month,
    filter_year,
    pivot_delays,
    statistics,
)
from .loading import LoadError, load_files
from .plotting import heatmap_figure, save_figure
from .processing import DEFAULT_MAX_DELAY_MINUTES, ProcessingReport, process

log = logging.getLogger(__name__)

FILE_TYPES = [
    ("All supported files", "*.csv *.txt *.xlsx *.xlsm *.xls"),
    ("CSV files", "*.csv *.txt"),
    ("Excel files", "*.xlsx *.xlsm *.xls"),
    ("All files", "*.*"),
]
IMAGE_TYPES = [("PNG image", "*.png"), ("PDF document", "*.pdf"), ("SVG image", "*.svg")]
DATA_TYPES = [("CSV file", "*.csv"), ("Excel file", "*.xlsx")]
PROFILES = (
    ("timeline", "Timeline (date × hour)"),
    ("weekday", "Weekday profile"),
    ("month", "Month profile"),
)
WEEK_BUTTONS_PER_ROW = 18
POLL_INTERVAL_MS = 50

HELP_TEXT = f"""Deployment Analyzer {__version__}

Analyzes the delay between the arrival of an image (time of day in the IPTC
instruction field) and its activation in the editorial system.

Getting started
  1. Click "Import" and select one or more export files (CSV or Excel).
  2. The heatmap shows the average delay per date and hour of arrival.
  3. Use "+ Add" to merge further export files into the current data set.

Navigation
  All data      the whole data set, one row per date
  Year          one row per date of that year
  Month         one row per date of that month
  Week          one row per date of that ISO week (W01 ... W53)

View
  Timeline         rows are dates (see above)
  Weekday profile  rows are Monday to Sunday, averaged over the selection
  Month profile    rows are January to December, averaged over the selection

Reading the heatmap
  Columns are hours of arrival (0-23). Red cells mean long delays, green
  cells short delays; white cells have no data. The colour scale is clipped
  to robust percentiles so that single outliers do not hide the pattern.

Export
  "Export image" saves the current heatmap (PNG, PDF or SVG).
  "Export data" saves the processed rows of the current selection
  (CSV or Excel), including the computed delay in minutes.
"""


@dataclass(frozen=True)
class View:
    """What the heatmap currently shows."""

    kind: str = "all"  # all | year | month | week
    year: int | None = None
    month: int | None = None
    iso_year: int | None = None
    iso_week: int | None = None

    def describe(self) -> str:
        if self.kind == "year":
            return str(self.year)
        if self.kind == "month":
            return f"{MONTH_LABELS[self.month - 1]} {self.year}"
        if self.kind == "week":
            return f"ISO week {self.iso_week}, {self.iso_year}"
        return "all data"

    def slug(self) -> str:
        return self.describe().lower().replace(" ", "_").replace(",", "")


class AnalyzerApp:
    """Main window."""

    def __init__(
        self,
        root: tk.Tk,
        files: Sequence[str | Path] = (),
        max_delay_minutes: float = DEFAULT_MAX_DELAY_MINUTES,
    ) -> None:
        self.root = root
        self.max_delay_minutes = max_delay_minutes
        self.data: pd.DataFrame | None = None
        self.loaded_files: list[str] = []
        self.fingerprints: set[str] = set()
        self.results: queue.Queue = queue.Queue()
        self.periods = Periods()
        self.view = View()
        self.current_figure = None
        self.figure_canvas: FigureCanvasTkAgg | None = None
        self.profile = tk.StringVar(value="timeline")
        self.status = tk.StringVar(value="Import an export file to start.")
        self.files_text = tk.StringVar(value="No files loaded")
        self.stats_text = tk.StringVar(value="")

        root.title(f"Deployment Analyzer {__version__}")
        root.geometry(
            f"{int(root.winfo_screenwidth() * 0.9)}x{int(root.winfo_screenheight() * 0.85)}"
        )
        root.minsize(900, 600)
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.report_callback_exception = self._report_callback_exception
        bold = tkfont.nametofont("TkDefaultFont").copy()
        bold.configure(weight="bold")
        self._bold_font = bold  # keep a reference; Tk drops unreferenced fonts
        ttk.Style(root).configure("Active.TButton", font=bold)

        self._build_widgets()
        if files:
            root.after(100, lambda: self.load_files([str(path) for path in files], replace=True))

    # ------------------------------------------------------------------ widgets
    def _build_widgets(self) -> None:
        root = self.root
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        top = ttk.Frame(root, padding=5)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(2, weight=1)

        self.import_button = ttk.Button(top, text="Import", command=self.import_files)
        self.import_button.grid(row=0, column=0, padx=(0, 4))
        self.add_button = ttk.Button(top, text="+ Add", command=self.add_files, state="disabled")
        self.add_button.grid(row=0, column=1, padx=(0, 12))
        ttk.Label(top, textvariable=self.files_text).grid(row=0, column=2, sticky="w")
        ttk.Label(top, textvariable=self.stats_text).grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(4, 0)
        )

        self.canvas_frame = ttk.Frame(root)
        self.canvas_frame.grid(row=1, column=0, sticky="nsew", padx=5)

        bottom = ttk.Frame(root, padding=5)
        bottom.grid(row=2, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=1)

        nav = ttk.LabelFrame(bottom, text="Period")
        nav.grid(row=0, column=0, sticky="ew")
        nav.columnconfigure(1, weight=1)
        self.year_buttons = self._navigation_row(nav, 0, "Years:")
        self.month_buttons = self._navigation_row(nav, 1, "Months:")
        self.week_buttons = self._navigation_row(nav, 2, "Weeks:")

        side = ttk.Frame(bottom)
        side.grid(row=0, column=1, sticky="ns", padx=(8, 0))
        view_box = ttk.LabelFrame(side, text="View")
        view_box.pack(fill="x")
        for value, label in PROFILES:
            ttk.Radiobutton(
                view_box, text=label, value=value, variable=self.profile, command=self.render
            ).pack(anchor="w")
        ttk.Button(side, text="Export image", command=self.export_image).pack(fill="x", pady=(6, 2))
        ttk.Button(side, text="Export data", command=self.export_data).pack(fill="x", pady=2)
        ttk.Button(side, text="Help", command=self.show_help).pack(fill="x", pady=2)

        status_bar = ttk.Frame(root)
        status_bar.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 4))
        status_bar.columnconfigure(0, weight=1)
        ttk.Label(status_bar, textvariable=self.status).grid(row=0, column=0, sticky="w")
        self.progress = ttk.Progressbar(status_bar, mode="indeterminate", length=160)
        self.progress.grid(row=0, column=1, sticky="e")

    @staticmethod
    def _navigation_row(parent: ttk.LabelFrame, row: int, label: str) -> ttk.Frame:
        ttk.Label(parent, text=label, width=8).grid(row=row, column=0, sticky="nw", padx=4, pady=2)
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=1, sticky="ew", pady=2)
        return frame

    def _rebuild_navigation(self) -> None:
        for frame in (self.year_buttons, self.month_buttons, self.week_buttons):
            for child in frame.winfo_children():
                child.destroy()
        if self.data is None:
            return
        view = self.view
        selected_year = view.year if view.kind != "all" else None

        self._button(self.year_buttons, "All data", View(), active=view.kind == "all").grid(
            row=0, column=0, padx=2
        )
        for column, year in enumerate(self.periods.years, start=1):
            self._button(
                self.year_buttons,
                str(year),
                View("year", year=year),
                active=view.kind == "year" and view.year == year,
            ).grid(row=0, column=column, padx=2)

        for column, month in enumerate(self.periods.months.get(selected_year, [])):
            active = view.kind == "month" and view.month == month
            self._button(
                self.month_buttons,
                MONTH_LABELS[month - 1],
                View("month", year=selected_year, month=month),
                active=active,
            ).grid(row=0, column=column, padx=2)

        for index, (iso_year, iso_week) in enumerate(self.periods.weeks.get(selected_year, [])):
            label = (
                f"W{iso_week:02d}"
                if iso_year == selected_year
                else f"W{iso_week:02d}/{iso_year % 100:02d}"
            )
            active = view.kind == "week" and view.iso_year == iso_year and view.iso_week == iso_week
            target = View("week", year=selected_year, iso_year=iso_year, iso_week=iso_week)
            self._button(self.week_buttons, label, target, active=active, width=7).grid(
                row=index // WEEK_BUTTONS_PER_ROW,
                column=index % WEEK_BUTTONS_PER_ROW,
                padx=1,
                pady=1,
            )

    def _button(
        self, parent: ttk.Frame, text: str, target: View, active: bool, width: int | None = None
    ):
        button = ttk.Button(parent, text=text, command=lambda: self.select(target))
        if width:
            button.configure(width=width)
        if active:
            button.configure(style="Active.TButton")
        return button

    # ------------------------------------------------------------------ loading
    def import_files(self) -> None:
        paths = self.root.tk.splitlist(
            filedialog.askopenfilenames(title="Import export files", filetypes=FILE_TYPES)
        )
        if paths:
            self.load_files(list(paths), replace=True)

    def add_files(self) -> None:
        paths = self.root.tk.splitlist(
            filedialog.askopenfilenames(title="Add export files", filetypes=FILE_TYPES)
        )
        if paths:
            self.load_files(list(paths), replace=False)

    def load_files(self, paths: list[str], replace: bool) -> None:
        self._set_busy(True, f"Loading {len(paths)} file(s) …")
        seen = set() if replace else set(self.fingerprints)
        worker = threading.Thread(
            target=self._load_worker, args=(paths, replace, seen), daemon=True
        )
        worker.start()
        self.root.after(POLL_INTERVAL_MS, self._poll_results)

    def _load_worker(self, paths: list[str], replace: bool, seen: set[str]) -> None:
        """Runs in a worker thread; must not call Tk."""
        try:
            raw = load_files(paths, seen=seen)
            data, report = process(raw, self.max_delay_minutes)
        except Exception as exc:
            log.exception("loading failed")
            self.results.put((self._on_load_failed, (exc,)))
            return
        used = list(dict.fromkeys(raw["source_file"]))
        self.results.put((self._on_loaded, (used, data, report, replace, seen)))

    def _poll_results(self) -> None:
        try:
            callback, args = self.results.get_nowait()
        except queue.Empty:
            self.root.after(POLL_INTERVAL_MS, self._poll_results)
            return
        callback(*args)

    def _on_loaded(
        self,
        paths: list[str],
        data: pd.DataFrame,
        report: ProcessingReport,
        replace: bool,
        fingerprints: set[str],
    ) -> None:
        self.fingerprints = fingerprints
        if replace or self.data is None:
            self.data = data
            self.loaded_files = list(paths)
        else:
            self.data = pd.concat([self.data, data], ignore_index=True)
            self.loaded_files.extend(paths)
        self.periods = available_periods(self.data)
        self.view = View()
        names = ", ".join(Path(path).name for path in self.loaded_files)
        self.files_text.set(f"{len(self.loaded_files)} file(s): {names}")
        self.add_button.configure(state="normal")
        self._set_busy(
            False,
            f"Loaded {report.rows_out:,} records; {report.dropped:,} rows dropped "
            f"({report.dropped_unparseable} unparseable, {report.dropped_negative} negative, "
            f"{report.dropped_above_max} above {self.max_delay_minutes:.0f} min)",
        )
        if self.data.empty:
            messagebox.showwarning(
                "No usable data", "None of the rows contained usable timestamps."
            )
        self.render()

    def _on_load_failed(self, exc: Exception) -> None:
        self._set_busy(False, "Loading failed")
        title = "Import error" if isinstance(exc, LoadError | ValueError) else "Unexpected error"
        messagebox.showerror(title, str(exc))

    # ------------------------------------------------------------------ rendering
    def select(self, view: View) -> None:
        self.view = view
        self.render()

    def selection(self) -> pd.DataFrame:
        if self.data is None:
            return pd.DataFrame()
        view = self.view
        if view.kind == "year":
            return filter_year(self.data, view.year)
        if view.kind == "month":
            return filter_month(self.data, view.year, view.month)
        if view.kind == "week":
            return filter_iso_week(self.data, view.iso_year, view.iso_week)
        return self.data

    def granularity(self) -> Granularity:
        profile = self.profile.get()
        if profile == "weekday":
            return "weekly"
        if profile == "month":
            return "monthly"
        return "daily" if self.view.kind in ("month", "week") else "yearly"

    def render(self) -> None:
        if self.data is None:
            return
        subset = self.selection()
        granularity = self.granularity()
        profile_label = dict(PROFILES)[self.profile.get()]
        subtitle = f"{self.view.describe()} – {profile_label}"
        fig = heatmap_figure(pivot_delays(subset, granularity), granularity, subtitle=subtitle)
        self._show_figure(fig)
        self._update_statistics(subset)
        self._rebuild_navigation()
        self.status.set(f"Showing {self.view.describe()}")

    def _show_figure(self, fig) -> None:
        for child in self.canvas_frame.winfo_children():
            child.destroy()
        self.current_figure = fig
        self.figure_canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        toolbar = NavigationToolbar2Tk(self.figure_canvas, self.canvas_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side="bottom", fill="x")
        self.figure_canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.figure_canvas.draw_idle()

    def _update_statistics(self, subset: pd.DataFrame) -> None:
        stats = statistics(subset)
        self.stats_text.set(
            f"Records: {stats['total_records']:,}   Average: {stats['avg_delay']:.1f} min   "
            f"Median: {stats['median_delay']:.1f} min   "
            f"95th percentile: {stats['p95_delay']:.1f} min   "
            f"Max: {stats['max_delay']:.1f} min"
        )

    def _set_busy(self, busy: bool, message: str) -> None:
        self.status.set(message)
        state = "disabled" if busy else "normal"
        self.import_button.configure(state=state)
        if self.data is not None:
            self.add_button.configure(state=state)
        if busy:
            self.progress.start(15)
        else:
            self.progress.stop()
            self.progress["value"] = 0

    # ------------------------------------------------------------------ export
    def _default_name(self, prefix: str, extension: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{self.view.slug()}_{self.profile.get()}_{timestamp}{extension}"

    def export_image(self) -> None:
        if self.current_figure is None:
            messagebox.showinfo("Nothing to export", "Import a file first.")
            return
        path = filedialog.asksaveasfilename(
            title="Export heatmap",
            defaultextension=".png",
            initialfile=self._default_name("heatmap", ".png"),
            filetypes=IMAGE_TYPES,
        )
        if path:
            save_figure(self.current_figure, path)
            self.status.set(f"Heatmap written to {path}")

    def export_data(self) -> None:
        subset = self.selection()
        if subset.empty:
            messagebox.showinfo("Nothing to export", "Import a file first.")
            return
        path = filedialog.asksaveasfilename(
            title="Export processed data",
            defaultextension=".csv",
            initialfile=self._default_name("data", ".csv"),
            filetypes=DATA_TYPES,
        )
        if not path:
            return
        if path.lower().endswith(".xlsx"):
            subset.to_excel(path, index=False)
        else:
            subset.to_csv(path, index=False)
        self.status.set(f"{len(subset):,} rows written to {path}")

    # ------------------------------------------------------------------ misc
    def show_help(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("Help")
        window.geometry("720x640")
        text = tk.Text(window, wrap="word", padx=12, pady=8)
        scrollbar = ttk.Scrollbar(window, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        text.insert("1.0", HELP_TEXT)
        text.configure(state="disabled")
        scrollbar.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)

    def _report_callback_exception(self, exc_type, exc_value, exc_tb) -> None:
        log.error("unhandled error in GUI callback", exc_info=(exc_type, exc_value, exc_tb))
        details = "".join(traceback.format_exception_only(exc_type, exc_value)).strip()
        messagebox.showerror("Unexpected error", details)

    def close(self) -> None:
        self.root.destroy()

    def with_view(self, **changes) -> View:
        """Helper for tests: a copy of the current view with fields replaced."""
        return replace(self.view, **changes)


def run_gui(
    files: Sequence[str | Path] = (), max_delay_minutes: float = DEFAULT_MAX_DELAY_MINUTES
) -> int:
    root = tk.Tk()
    AnalyzerApp(root, files, max_delay_minutes=max_delay_minutes)
    root.mainloop()
    return 0
