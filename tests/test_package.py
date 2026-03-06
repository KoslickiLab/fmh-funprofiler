"""
Tests that the package is importable, has the correct version, and exposes
the expected public API and CLI entry points.
"""

import subprocess
import sys


def test_package_imports():
    import fmh_funprofiler  # noqa: F401


def test_version():
    import fmh_funprofiler

    assert fmh_funprofiler.__version__ == "1.1.0"


def test_funcprofiler_importable():
    from fmh_funprofiler.funcprofiler import (  # noqa: F401
        check_args,
        create_sketch,
        main,
        parse_args,
        sanity_check,
    )


def test_funcprofiler_many_importable():
    from fmh_funprofiler.funcprofiler_many import (  # noqa: F401
        check_args,
        main,
        parse_arguments,
        run_funcprofiler,
    )


def test_funcprofiler_help_flag():
    """funcprofiler --help should exit 0 and print usage."""
    result = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.argv = ['funcprofiler', '--help']; "
         "from fmh_funprofiler.funcprofiler import parse_args; parse_args()"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "metagenome" in result.stdout.lower()


def test_funcprofiler_many_help_flag():
    """funcprofiler-many --help should exit 0 and print usage."""
    result = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.argv = ['funcprofiler-many', '--help']; "
         "from fmh_funprofiler.funcprofiler_many import parse_arguments; parse_arguments()"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "metagenome" in result.stdout.lower()
