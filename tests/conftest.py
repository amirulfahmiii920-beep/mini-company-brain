"""Shared pytest fixtures."""

import secrets
from collections.abc import Iterator

import psycopg
import pytest

from mini_company_brain.config import load_settings
from mini_company_brain.db import apply_schema, connect


@pytest.fixture
def db_conn() -> Iterator[psycopg.Connection]:
    """A connection whose tables live in a throwaway schema.

    Each test gets its own schema named test_<random>, so tests never read or
    change real ingested data. The vector extension stays in `public`, which is
    why `public` is kept on the search_path.
    """
    schema = f"test_{secrets.token_hex(4)}"
    conn = connect(load_settings())
    conn.autocommit = True
    try:
        conn.execute(f"CREATE SCHEMA {schema}")
        conn.execute(f"SET search_path TO {schema}, public")
        apply_schema(conn)
        yield conn
    finally:
        conn.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
        conn.close()
