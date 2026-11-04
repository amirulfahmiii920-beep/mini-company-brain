"""Settings read from the environment (.env in development)."""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from psycopg.conninfo import make_conninfo

# docker-compose.yml publishes Postgres on localhost only.
DB_HOST = "127.0.0.1"
DEFAULT_DB_PORT = "5432"

# Repo root, so the model cache stays inside the project on D: by default.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_CACHE_DIR = PROJECT_ROOT / ".cache" / "fastembed"


class ConfigError(RuntimeError):
    """A required setting is missing. The message names the variable, never its value."""


@dataclass(frozen=True)
class Settings:
    # repr=False: the connection string contains the password, and dataclass
    # reprs show up in tracebacks and debug logs.
    database_url: str = field(repr=False)
    model_cache_dir: Path


def _require(env: Mapping[str, str], name: str) -> str:
    value = env.get(name, "")
    if not value:
        raise ConfigError(f"{name} is not set. Copy .env.example to .env and fill it in.")
    return value


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Build Settings from `env`, or from .env plus the process environment when `env` is None.

    Passing `env` explicitly keeps tests independent of the developer's real .env file.
    """
    if env is None:
        load_dotenv()
        env = os.environ

    # make_conninfo quotes values safely, so a password with spaces or quotes still works.
    database_url = make_conninfo(
        host=DB_HOST,
        port=env.get("POSTGRES_PORT") or DEFAULT_DB_PORT,
        user=_require(env, "POSTGRES_USER"),
        password=_require(env, "POSTGRES_PASSWORD"),
        dbname=_require(env, "POSTGRES_DB"),
    )
    cache_dir = env.get("FASTEMBED_CACHE_DIR")
    return Settings(
        database_url=database_url,
        model_cache_dir=Path(cache_dir) if cache_dir else DEFAULT_MODEL_CACHE_DIR,
    )
