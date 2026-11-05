"""Tests for the command-line error handling (no database needed)."""

import pytest

from mini_company_brain.cli import ingest_main, search_main


def test_missing_setting_exits_1_with_clear_message(monkeypatch, capsys):
    # load_dotenv never overrides a variable that is already set, so the real
    # .env cannot fill this back in.
    monkeypatch.setenv("POSTGRES_PASSWORD", "")
    assert ingest_main([]) == 1
    err = capsys.readouterr().err
    assert "POSTGRES_PASSWORD is not set" in err
    assert "Traceback" not in err


def test_search_rejects_unknown_role(capsys):
    # argparse exits with code 2 for invalid arguments, before any connection.
    with pytest.raises(SystemExit) as exc:
        search_main(["annual leave", "--role", "admin"])
    assert exc.value.code == 2
    assert "invalid choice: 'admin'" in capsys.readouterr().err


def test_search_role_defaults_to_employee(monkeypatch, capsys):
    # Least privilege: without --role, HR-only chunks must not be searchable.
    # The run stops at the missing setting, after parsing; the message proves
    # nothing was printed as an HR search.
    monkeypatch.setenv("POSTGRES_PASSWORD", "")
    assert search_main(["annual leave"]) == 1
    assert "role: employee" in capsys.readouterr().out


def test_search_empty_query_exits_1(capsys):
    assert search_main(["   "]) == 1
    assert "query must not be empty" in capsys.readouterr().err
