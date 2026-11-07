"""Tests for database connection errors (no database needed)."""

import socket
import traceback

import pytest

from mini_company_brain.cli import ingest_main
from mini_company_brain.config import load_settings
from mini_company_brain.db import DatabaseConnectionError, connect

FAKE_PASSWORD = "never-print-this-9f3k"


def _unused_port() -> int:
    # Port 0 asks the OS for any free port. Once the socket closes, nothing
    # listens there, so a connection to it fails.
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="module")
def connect_error() -> Exception:
    """One failed connect() shared by the tests below. On Windows each attempt
    waits for the 5 second connect timeout, so it runs only once."""
    settings = load_settings(
        {
            "POSTGRES_USER": "brain",
            "POSTGRES_PASSWORD": FAKE_PASSWORD,
            "POSTGRES_DB": "brain_db",
            "POSTGRES_PORT": str(_unused_port()),
        }
    )
    try:
        connect(settings)
    except Exception as exc:
        return exc
    pytest.fail("connect() should fail when nothing listens on the port")


def test_failed_connection_never_shows_password(connect_error):
    python_traceback = "".join(traceback.format_exception(connect_error))
    # pytest's failure report also prints the arguments (and here the locals) of
    # every frame. That is how the real password leaked before this fix.
    pytest_report = str(
        pytest.ExceptionInfo.from_exception(connect_error).getrepr(
            style="long", funcargs=True, showlocals=True
        )
    )
    assert FAKE_PASSWORD not in python_traceback
    assert FAKE_PASSWORD not in pytest_report


def test_failed_connection_raises_clean_error(connect_error):
    assert isinstance(connect_error, DatabaseConnectionError)
    assert "Is Docker running?" in str(connect_error)
    # `raise ... from None`: the psycopg error, whose frames hold the connection
    # string, is not attached for tracebacks to print.
    assert connect_error.__cause__ is None
    assert connect_error.__suppress_context__


def test_cli_reports_failed_connection_in_one_line(monkeypatch, capsys):
    # load_dotenv never overrides variables that are already set, so the real
    # .env cannot change these.
    monkeypatch.setenv("POSTGRES_PASSWORD", FAKE_PASSWORD)
    monkeypatch.setenv("POSTGRES_PORT", str(_unused_port()))
    assert ingest_main([]) == 1
    captured = capsys.readouterr()
    assert "Error: Cannot connect to Postgres" in captured.err
    assert "Traceback" not in captured.err
    assert FAKE_PASSWORD not in captured.out + captured.err
