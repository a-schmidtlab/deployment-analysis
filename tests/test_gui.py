"""Smoke test of the GUI; skipped where Tk or a display is unavailable."""

import time

import pytest

tk = pytest.importorskip("tkinter")


@pytest.fixture
def root():
    try:
        window = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"no display: {exc}")
    window.withdraw()
    yield window
    window.destroy()


def test_app_loads_file_and_renders(root, csv_path):
    from deployment_analyzer.gui import AnalyzerApp, View

    app = AnalyzerApp(root)
    app.load_files([str(csv_path)], replace=True)
    deadline = time.monotonic() + 30
    while app.data is None and time.monotonic() < deadline:  # pump the event loop
        root.update()
        time.sleep(0.02)
    assert app.data is not None and not app.data.empty
    assert app.current_figure is not None
    assert app.periods.years == [2025]

    app.select(View("week", year=2025, iso_year=2025, iso_week=6))
    root.update()
    assert app.granularity() == "daily"
    assert "ISO week 6" in app.status.get()
    app.profile.set("weekday")
    app.render()
    assert app.granularity() == "weekly"
    assert len(app.week_buttons.winfo_children()) == 3


def test_app_skips_duplicate_on_add(root, csv_path, tmp_path):
    from deployment_analyzer.gui import AnalyzerApp

    app = AnalyzerApp(root)

    def wait():
        deadline = time.monotonic() + 30
        while str(app.import_button.cget("state")) == "disabled" and time.monotonic() < deadline:
            root.update()
            time.sleep(0.02)

    app.load_files([str(csv_path)], replace=True)
    wait()
    rows = len(app.data)
    copy = tmp_path / "copy.csv"
    copy.write_bytes(csv_path.read_bytes())
    app._on_load_failed = lambda exc: app.status.set(f"failed: {exc}")
    app.load_files([str(copy)], replace=False)
    wait()
    assert len(app.data) == rows
    assert "duplicates" in app.status.get()


def test_cli_self_test(root):
    from deployment_analyzer.cli import main

    assert main(["--self-test"]) == 0
