"""Reading raw export files (CSV or Excel) into DataFrames.

CSV exports vary in delimiter (``;`` or ``,``), encoding (UTF-8 with or
without BOM, Windows-1252) and sometimes lack the header row. All of that is
detected here so that the rest of the package only ever sees a DataFrame with
the known column names (see :mod:`deployment_analyzer.processing`).
"""

from __future__ import annotations

import csv
import hashlib
import logging
from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from .processing import EXPECTED_COLUMNS, KNOWN_COLUMNS

log = logging.getLogger(__name__)

ENCODINGS = ("utf-8-sig", "cp1252", "latin-1")
DELIMITERS = (";", ",", "\t")
CSV_SUFFIXES = {".csv", ".txt"}
EXCEL_SUFFIXES = {".xlsx", ".xlsm", ".xls"}
SOURCE_COLUMN = "source_file"


class LoadError(ValueError):
    """Raised when a file cannot be read as an export."""


def detect_encoding(path: Path) -> str:
    """Return the first encoding from :data:`ENCODINGS` that decodes the file."""
    for encoding in ENCODINGS:
        try:
            with open(path, encoding=encoding) as handle:
                handle.read()
            return encoding
        except UnicodeDecodeError:
            continue
    return ENCODINGS[-1]


def detect_delimiter(line: str) -> str:
    """Pick the delimiter that occurs most often in ``line`` (default ``,``)."""
    counts = {delimiter: line.count(delimiter) for delimiter in DELIMITERS}
    best = max(counts, key=counts.__getitem__)
    return best if counts[best] > 0 else ","


def has_header(line: str, delimiter: str) -> bool:
    """True if ``line`` contains at least one known column name."""
    cells = next(csv.reader([line], delimiter=delimiter), [])
    return any(cell.strip() in KNOWN_COLUMNS for cell in cells)


def read_csv(path: str | Path, encoding: str | None = None, delimiter: str | None = None):
    """Read a CSV export, detecting encoding, delimiter and a missing header."""
    path = Path(path)
    encoding = encoding or detect_encoding(path)
    with open(path, encoding=encoding, newline="") as handle:
        first_line = handle.readline()
    if not first_line.strip():
        raise LoadError(f"{path.name}: file is empty")
    delimiter = delimiter or detect_delimiter(first_line)
    options = {"sep": delimiter, "encoding": encoding, "dtype": str}

    if has_header(first_line, delimiter):
        frame = pd.read_csv(path, **options)
    else:
        frame = pd.read_csv(path, header=None, **options)
        if frame.shape[1] != len(EXPECTED_COLUMNS):
            raise LoadError(
                f"{path.name}: no header row and {frame.shape[1]} columns; "
                f"expected {len(EXPECTED_COLUMNS)} ({', '.join(EXPECTED_COLUMNS)})"
            )
        frame.columns = list(EXPECTED_COLUMNS)
        log.warning("%s: no header row found, assuming the standard column order", path.name)

    frame.columns = [str(column).strip() for column in frame.columns]
    frame = frame.dropna(how="all").reset_index(drop=True)
    log.info("%s: %d rows (encoding %s, delimiter %r)", path.name, len(frame), encoding, delimiter)
    return frame


def read_excel(path: str | Path):
    """Read the first sheet of an Excel export."""
    path = Path(path)
    frame = pd.read_excel(path)
    frame.columns = [str(column).strip() for column in frame.columns]
    frame = frame.dropna(how="all").reset_index(drop=True)
    log.info("%s: %d rows", path.name, len(frame))
    return frame


def load_file(path: str | Path):
    """Read one export file; the format is chosen by file extension."""
    path = Path(path)
    if not path.is_file():
        raise LoadError(f"{path}: file not found")
    suffix = path.suffix.lower()
    if suffix in CSV_SUFFIXES:
        return read_csv(path)
    if suffix in EXCEL_SUFFIXES:
        return read_excel(path)
    raise LoadError(f"{path.name}: unsupported file type {suffix!r}")


def fingerprint(frame: pd.DataFrame) -> str:
    """Content hash of an export, independent of header row, delimiter and encoding."""
    columns = [column for column in frame.columns if column != SOURCE_COLUMN]
    values = frame[columns].astype(str)
    hashes = pd.util.hash_pandas_object(values, index=False).to_numpy()
    return hashlib.sha256(hashes.tobytes()).hexdigest()


def load_files(paths: Iterable[str | Path], seen: set[str] | None = None):
    """Read several export files and concatenate them.

    The resulting frame carries the originating file name in the
    ``source_file`` column. A file whose content equals a file loaded before
    (in this call or, via ``seen``, in an earlier one) is skipped with a
    warning; ``seen`` is updated in place.
    """
    seen = set() if seen is None else seen
    frames = []
    for path in paths:
        frame = load_file(path)
        key = fingerprint(frame)
        if key in seen:
            log.warning("%s: same content as a file already loaded, skipped", Path(path).name)
            continue
        seen.add(key)
        frame[SOURCE_COLUMN] = Path(path).name
        frames.append(frame)
    if not frames:
        raise LoadError("no new input files (none given, or all duplicates of loaded files)")
    return pd.concat(frames, ignore_index=True)
