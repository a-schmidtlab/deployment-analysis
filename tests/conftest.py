import pandas as pd
import pytest

from deployment_analyzer.sampledata import generate_export, generate_timestamps, to_export_rows


@pytest.fixture(scope="session")
def export_frame() -> pd.DataFrame:
    """Synthetic export rows (three weeks, ~2000 images)."""
    return generate_export(n=2000, start="2025-02-03", days=21, seed=7)


@pytest.fixture(scope="session")
def timestamps() -> pd.DataFrame:
    return generate_timestamps(n=2000, start="2025-02-03", days=21, seed=7)


def write_export(path, frame: pd.DataFrame, delimiter=";", encoding="utf-8", header=True) -> None:
    frame.to_csv(path, sep=delimiter, index=False, encoding=encoding, header=header)


@pytest.fixture
def csv_path(tmp_path, export_frame):
    path = tmp_path / "export.csv"
    write_export(path, export_frame)
    return path


def export_from_pairs(pairs: list[tuple[str, str]]) -> pd.DataFrame:
    """Export rows from explicit ``(arrival, activation)`` ISO timestamps."""
    frame = pd.DataFrame(
        {
            "arrival": pd.to_datetime([a for a, _ in pairs]),
            "activation": pd.to_datetime([b for _, b in pairs]),
        }
    )
    return to_export_rows(frame)
