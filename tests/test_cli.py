import pandas as pd
import pytest

from deployment_analyzer.cli import describe_period, format_statistics, main, select_period
from deployment_analyzer.processing import DELAY, process


def test_batch_writes_outputs(csv_path, tmp_path, capsys):
    heatmap = tmp_path / "out" / "heatmap.png"
    export = tmp_path / "out" / "rows.csv"
    assert (
        main([str(csv_path), "-o", str(heatmap), "--export-csv", str(export), "-g", "weekly"]) == 0
    )
    assert heatmap.is_file()
    assert DELAY in pd.read_csv(export).columns
    out = capsys.readouterr().out
    assert "Records" in out and "Heatmap written" in out


def test_batch_period_filters(csv_path, tmp_path, capsys):
    assert (
        main([str(csv_path), "--year", "2025", "--week", "6", "-o", str(tmp_path / "w.png")]) == 0
    )
    assert "ISO week 6, 2025" in capsys.readouterr().out
    assert main([str(csv_path), "--year", "2025", "--month", "2"]) == 0
    assert main([str(csv_path), "--year", "1999"]) == 1
    assert main([str(csv_path), "--month", "2"]) == 2
    assert "requires --year" in capsys.readouterr().err


def test_batch_errors(tmp_path, capsys):
    assert main([str(tmp_path / "missing.csv")]) == 2
    assert "not found" in capsys.readouterr().err


def test_version(capsys):
    with pytest.raises(SystemExit) as info:
        main(["--version"])
    assert info.value.code == 0
    assert "deployment-analyzer" in capsys.readouterr().out


def test_select_and_describe_period(export_frame):
    data = process(export_frame)[0]
    assert len(select_period(data, None, None, None)) == len(data)
    assert len(select_period(data, 2025, 2, None)) == len(data)
    assert select_period(data, 2024, None, None).empty
    assert describe_period(2025, None, 6) == "ISO week 6, 2025"
    assert describe_period(2025, 2, None) == "2025-02"
    assert describe_period(None, None, None) is None


def test_format_statistics():
    text = format_statistics(
        {
            "total_records": 1234,
            "avg_delay": 1.25,
            "median_delay": 1,
            "min_delay": 0,
            "max_delay": 9,
            "p95_delay": 4,
        }
    )
    assert "1,234" in text and "1.2 min" in text
