"""
Unit tests for fmh_funprofiler.funcprofiler.

Tests focus on argument validation (check_args) and argument parsing (parse_args),
which are the testable units that do not require sourmash or real sketch files.
"""

import argparse
import sys

import pytest

from fmh_funprofiler.funcprofiler import check_args, parse_args


def _make_args(mg_filename, ko_sketch, ksize=11, scaled=1000, threshold_bp=1000):
    """Return a Namespace that mirrors what parse_args() would produce."""
    return argparse.Namespace(
        mg_filename=mg_filename,
        ko_sketch=ko_sketch,
        ksize=ksize,
        scaled=scaled,
        threshold_bp=threshold_bp,
        prefetch_file=None,
    )


# ---------------------------------------------------------------------------
# check_args – file existence
# ---------------------------------------------------------------------------

def test_check_args_missing_metagenome(tmp_path):
    """Exits when the metagenome file does not exist."""
    ko = tmp_path / "ref.sig.zip"
    ko.write_bytes(b"")
    args = _make_args(mg_filename=str(tmp_path / "missing.fastq"), ko_sketch=str(ko))
    with pytest.raises(SystemExit) as exc:
        check_args(args)
    assert exc.value.code == 1


def test_check_args_missing_ko_sketch(tmp_path):
    """Exits when the KO sketch file does not exist."""
    mg = tmp_path / "sample.fastq"
    mg.write_bytes(b"")
    args = _make_args(mg_filename=str(mg), ko_sketch=str(tmp_path / "missing.sig.zip"))
    with pytest.raises(SystemExit) as exc:
        check_args(args)
    assert exc.value.code == 1


# ---------------------------------------------------------------------------
# check_args – ksize validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ksize", [7, 11, 15])
def test_check_args_valid_ksize(tmp_path, ksize):
    """Valid ksize values (7, 11, 15) should not exit."""
    mg = tmp_path / "sample.fastq"
    ko = tmp_path / "ref.sig.zip"
    mg.write_bytes(b"")
    ko.write_bytes(b"")
    args = _make_args(mg_filename=str(mg), ko_sketch=str(ko), ksize=ksize)
    assert check_args(args) is True


@pytest.mark.parametrize("ksize", [0, 5, 10, 21, -1])
def test_check_args_invalid_ksize(tmp_path, ksize):
    """Invalid ksize values should cause SystemExit(1)."""
    mg = tmp_path / "sample.fastq"
    ko = tmp_path / "ref.sig.zip"
    mg.write_bytes(b"")
    ko.write_bytes(b"")
    args = _make_args(mg_filename=str(mg), ko_sketch=str(ko), ksize=ksize)
    with pytest.raises(SystemExit) as exc:
        check_args(args)
    assert exc.value.code == 1


# ---------------------------------------------------------------------------
# check_args – scaled validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("scaled", [1, 100, 500, 1000])
def test_check_args_valid_scaled(tmp_path, scaled):
    mg = tmp_path / "sample.fastq"
    ko = tmp_path / "ref.sig.zip"
    mg.write_bytes(b"")
    ko.write_bytes(b"")
    args = _make_args(mg_filename=str(mg), ko_sketch=str(ko), scaled=scaled)
    assert check_args(args) is True


@pytest.mark.parametrize("scaled", [0, -1, -100])
def test_check_args_invalid_scaled(tmp_path, scaled):
    mg = tmp_path / "sample.fastq"
    ko = tmp_path / "ref.sig.zip"
    mg.write_bytes(b"")
    ko.write_bytes(b"")
    args = _make_args(mg_filename=str(mg), ko_sketch=str(ko), scaled=scaled)
    with pytest.raises(SystemExit) as exc:
        check_args(args)
    assert exc.value.code == 1


# ---------------------------------------------------------------------------
# check_args – threshold_bp validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("threshold_bp", [1, 100, 1000])
def test_check_args_valid_threshold_bp(tmp_path, threshold_bp):
    mg = tmp_path / "sample.fastq"
    ko = tmp_path / "ref.sig.zip"
    mg.write_bytes(b"")
    ko.write_bytes(b"")
    args = _make_args(mg_filename=str(mg), ko_sketch=str(ko), threshold_bp=threshold_bp)
    assert check_args(args) is True


@pytest.mark.parametrize("threshold_bp", [0, -1, -500])
def test_check_args_invalid_threshold_bp(tmp_path, threshold_bp):
    mg = tmp_path / "sample.fastq"
    ko = tmp_path / "ref.sig.zip"
    mg.write_bytes(b"")
    ko.write_bytes(b"")
    args = _make_args(mg_filename=str(mg), ko_sketch=str(ko), threshold_bp=threshold_bp)
    with pytest.raises(SystemExit) as exc:
        check_args(args)
    assert exc.value.code == 1


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------

def test_parse_args_positional(tmp_path, monkeypatch):
    """parse_args reads positional arguments correctly from sys.argv."""
    monkeypatch.setattr(
        sys, "argv",
        ["funcprofiler", "sample.fastq", "ref.sig.zip", "11", "1000", "out.csv"],
    )
    args = parse_args()
    assert args.mg_filename == "sample.fastq"
    assert args.ko_sketch == "ref.sig.zip"
    assert args.ksize == 11
    assert args.scaled == 1000
    assert args.output == "out.csv"
    assert args.threshold_bp == 1000  # default
    assert args.prefetch_file is None  # default


def test_parse_args_optional_threshold(tmp_path, monkeypatch):
    monkeypatch.setattr(
        sys, "argv",
        ["funcprofiler", "sample.fastq", "ref.sig.zip", "7", "500", "out.csv", "-t", "50"],
    )
    args = parse_args()
    assert args.threshold_bp == 50


def test_parse_args_optional_prefetch(tmp_path, monkeypatch):
    monkeypatch.setattr(
        sys, "argv",
        ["funcprofiler", "sample.fastq", "ref.sig.zip", "15", "1000", "out.csv", "-p", "prefetch.csv"],
    )
    args = parse_args()
    assert args.prefetch_file == "prefetch.csv"
