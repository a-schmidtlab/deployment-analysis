import pandas as pd
import pytest
from conftest import write_export

from deployment_analyzer.loading import (
    SOURCE_COLUMN,
    LoadError,
    detect_delimiter,
    detect_encoding,
    fingerprint,
    has_header,
    load_file,
    load_files,
    read_csv,
)
from deployment_analyzer.processing import COL_ACTIVATION, COL_IPTC_DE, EXPECTED_COLUMNS


def test_detect_delimiter():
    assert detect_delimiter('"a";"b";"c"') == ";"
    assert detect_delimiter("a,b,c") == ","
    assert detect_delimiter("a\tb\tc") == "\t"
    assert detect_delimiter("abc") == ","


def test_has_header():
    assert has_header('"IPTC_DE Anweisung";"IPTC_EN Anweisung"', ";")
    assert not has_header(",,,,", ",")
    assert not has_header(
        "[23:33:11] World Rights,[23:33:11] World Rights,30.12.2024 23:36:26,Ja,"
        "30.12.2024 23:36:26",
        ",",
    )


@pytest.mark.parametrize("delimiter", [";", ","])
@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig", "cp1252"])
def test_read_csv_variants(tmp_path, export_frame, delimiter, encoding):
    path = tmp_path / "export.csv"
    write_export(path, export_frame, delimiter=delimiter, encoding=encoding)
    frame = read_csv(path)
    assert list(frame.columns) == list(EXPECTED_COLUMNS)
    assert len(frame) == len(export_frame)
    assert frame[COL_ACTIVATION].iloc[0] == export_frame[COL_ACTIVATION].iloc[0]


def test_detect_encoding(tmp_path, export_frame):
    path = tmp_path / "export.csv"
    write_export(path, export_frame, encoding="cp1252")
    assert detect_encoding(path) == "cp1252"
    write_export(path, export_frame, encoding="utf-8-sig")
    assert detect_encoding(path) == "utf-8-sig"


def test_read_csv_without_header(tmp_path, export_frame):
    """Exports occasionally come with an empty first line instead of a header."""
    path = tmp_path / "no head.csv"
    body = export_frame.head(20).to_csv(index=False, header=False)
    path.write_text(",,,,\n" + body, encoding="utf-8")
    frame = read_csv(path)
    assert list(frame.columns) == list(EXPECTED_COLUMNS)
    assert len(frame) == 20
    assert frame[COL_IPTC_DE].iloc[0].startswith("[")


def test_read_csv_without_header_wrong_width(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("1,2,3\n4,5,6\n", encoding="utf-8")
    with pytest.raises(LoadError, match="expected 5"):
        read_csv(path)


def test_read_csv_empty(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(LoadError, match="empty"):
        read_csv(path)


def test_load_file_excel(tmp_path, export_frame):
    path = tmp_path / "export.xlsx"
    export_frame.head(50).to_excel(path, index=False)
    frame = load_file(path)
    assert list(frame.columns) == list(EXPECTED_COLUMNS)
    assert len(frame) == 50


def test_load_file_errors(tmp_path):
    with pytest.raises(LoadError, match="not found"):
        load_file(tmp_path / "missing.csv")
    path = tmp_path / "export.json"
    path.write_text("{}")
    with pytest.raises(LoadError, match="unsupported"):
        load_file(path)


def test_load_files_concatenates(tmp_path, export_frame):
    first, second = tmp_path / "a.csv", tmp_path / "b.csv"
    write_export(first, export_frame.head(30))
    write_export(second, export_frame.tail(20), delimiter=",")
    frame = load_files([first, second])
    assert len(frame) == 50
    assert frame[SOURCE_COLUMN].value_counts().to_dict() == {"a.csv": 30, "b.csv": 20}
    assert isinstance(frame, pd.DataFrame)


def test_load_files_requires_input():
    with pytest.raises(LoadError):
        load_files([])


def test_fingerprint_ignores_format(tmp_path, export_frame):
    with_header, without_header = tmp_path / "a.csv", tmp_path / "b.csv"
    write_export(with_header, export_frame.head(40), delimiter=";", encoding="utf-8")
    without_header.write_text(
        ",,,,\n" + export_frame.head(40).to_csv(index=False, header=False), encoding="cp1252"
    )
    assert fingerprint(read_csv(with_header)) == fingerprint(read_csv(without_header))
    assert fingerprint(read_csv(with_header)) != fingerprint(export_frame.head(39))


def test_load_files_skips_duplicate_content(tmp_path, export_frame, caplog):
    first, copy, other = tmp_path / "a.csv", tmp_path / "copy.csv", tmp_path / "c.csv"
    write_export(first, export_frame.head(30))
    write_export(copy, export_frame.head(30), delimiter=",")
    write_export(other, export_frame.tail(10))
    frame = load_files([first, copy, other])
    assert len(frame) == 40
    assert "copy.csv: same content" in caplog.text

    seen: set[str] = set()
    load_files([first], seen=seen)
    assert len(load_files([copy, other], seen=seen)) == 10
    with pytest.raises(LoadError, match="duplicates"):
        load_files([first], seen=seen)
