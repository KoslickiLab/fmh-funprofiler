"""
Unit tests for fmh_funprofiler.funcprofiler_many.

Tests cover argument validation (check_args) and argument parsing (parse_arguments).
"""

import argparse
import sys

import pytest

from fmhfunprofiler.funcprofiler_many import check_args, parse_arguments


def _make_args(ko_sketch, ksize=11, scaled=1000, threshold_bp=1000, filelist="files.csv"):
    return argparse.Namespace(
        ko_sketch=ko_sketch,
        ksize=ksize,
        scaled=scaled,
        threshold_bp=threshold_bp,
        filelist=filelist,
    )


# ---------------------------------------------------------------------------
# check_args – ko_sketch existence
# ---------------------------------------------------------------------------

def test_check_args_missing_ko_sketch(tmp_path):
    args = _make_args(ko_sketch=str(tmp_path / "missing.sig.zip"))
    with pytest.raises(SystemExit) as exc:
        check_args(args)
    assert exc.value.code == 1


def test_check_args_existing_ko_sketch(tmp_path):
    ko = tmp_path / "ref.sig.zip"
    ko.write_bytes(b"")
    args = _make_args(ko_sketch=str(ko))
    assert check_args(args) is True


# ---------------------------------------------------------------------------
# check_args – ksize validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ksize", [7, 11, 15])
def test_check_args_valid_ksize(tmp_path, ksize):
    ko = tmp_path / "ref.sig.zip"
    ko.write_bytes(b"")
    args = _make_args(ko_sketch=str(ko), ksize=ksize)
    assert check_args(args) is True


@pytest.mark.parametrize("ksize", [0, 5, 10, 21, -1])
def test_check_args_invalid_ksize(tmp_path, ksize):
    ko = tmp_path / "ref.sig.zip"
    ko.write_bytes(b"")
    args = _make_args(ko_sketch=str(ko), ksize=ksize)
    with pytest.raises(SystemExit) as exc:
        check_args(args)
    assert exc.value.code == 1


# ---------------------------------------------------------------------------
# check_args – scaled validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("scaled", [1, 500, 1000])
def test_check_args_valid_scaled(tmp_path, scaled):
    ko = tmp_path / "ref.sig.zip"
    ko.write_bytes(b"")
    args = _make_args(ko_sketch=str(ko), scaled=scaled)
    assert check_args(args) is True


@pytest.mark.parametrize("scaled", [0, -1])
def test_check_args_invalid_scaled(tmp_path, scaled):
    ko = tmp_path / "ref.sig.zip"
    ko.write_bytes(b"")
    args = _make_args(ko_sketch=str(ko), scaled=scaled)
    with pytest.raises(SystemExit) as exc:
        check_args(args)
    assert exc.value.code == 1


# ---------------------------------------------------------------------------
# check_args – threshold_bp validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("threshold_bp", [1, 100, 1000])
def test_check_args_valid_threshold_bp(tmp_path, threshold_bp):
    ko = tmp_path / "ref.sig.zip"
    ko.write_bytes(b"")
    args = _make_args(ko_sketch=str(ko), threshold_bp=threshold_bp)
    assert check_args(args) is True


@pytest.mark.parametrize("threshold_bp", [0, -1])
def test_check_args_invalid_threshold_bp(tmp_path, threshold_bp):
    ko = tmp_path / "ref.sig.zip"
    ko.write_bytes(b"")
    args = _make_args(ko_sketch=str(ko), threshold_bp=threshold_bp)
    with pytest.raises(SystemExit) as exc:
        check_args(args)
    assert exc.value.code == 1


# ---------------------------------------------------------------------------
# parse_arguments
# ---------------------------------------------------------------------------

def test_parse_arguments(tmp_path, monkeypatch):
    monkeypatch.setattr(
        sys, "argv",
        ["funcprofiler-many", "ref.sig.zip", "11", "1000", "files.csv", "500"],
    )
    args = parse_arguments()
    assert args.ko_sketch == "ref.sig.zip"
    assert args.ksize == 11
    assert args.scaled == 1000
    assert args.filelist == "files.csv"
    assert args.threshold_bp == 500
