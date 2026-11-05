"""Tests for the mcb-ingest command's error handling (no database needed)."""

from mini_company_brain.cli import ingest_main


def test_missing_setting_exits_1_with_clear_message(monkeypatch, capsys):
    # load_dotenv never overrides a variable that is already set, so the real
    # .env cannot fill this back in.
    monkeypatch.setenv("POSTGRES_PASSWORD", "")
    assert ingest_main([]) == 1
    err = capsys.readouterr().err
    assert "POSTGRES_PASSWORD is not set" in err
    assert "Traceback" not in err
