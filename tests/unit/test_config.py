"""Tests for reading database settings from the environment."""

import pytest

from mini_company_brain.config import ConfigError, load_settings

FULL_ENV = {
    "POSTGRES_USER": "brain",
    "POSTGRES_PASSWORD": "s3cret-value",
    "POSTGRES_DB": "brain_db",
    "POSTGRES_PORT": "5433",
}


def test_builds_database_url_from_env():
    settings = load_settings(FULL_ENV)
    assert "user=brain" in settings.database_url
    assert "dbname=brain_db" in settings.database_url
    assert "port=5433" in settings.database_url
    assert "host=127.0.0.1" in settings.database_url


def test_database_url_has_connect_timeout():
    # Without it, connecting while Docker is stopped hangs for minutes on Windows.
    assert "connect_timeout=5" in load_settings(FULL_ENV).database_url


def test_port_defaults_to_5432():
    env = {k: v for k, v in FULL_ENV.items() if k != "POSTGRES_PORT"}
    assert "port=5432" in load_settings(env).database_url


@pytest.mark.parametrize("missing", ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"])
def test_missing_variable_names_it(missing):
    env = {k: v for k, v in FULL_ENV.items() if k != missing}
    with pytest.raises(ConfigError, match=missing):
        load_settings(env)


def test_empty_variable_counts_as_missing():
    with pytest.raises(ConfigError, match="POSTGRES_PASSWORD"):
        load_settings({**FULL_ENV, "POSTGRES_PASSWORD": ""})


def test_password_never_appears_in_repr():
    # Settings may end up in a traceback or a log line; the password must not.
    assert "s3cret-value" not in repr(load_settings(FULL_ENV))


def test_model_cache_dir_can_be_overridden(tmp_path):
    settings = load_settings({**FULL_ENV, "FASTEMBED_CACHE_DIR": str(tmp_path)})
    assert settings.model_cache_dir == tmp_path
