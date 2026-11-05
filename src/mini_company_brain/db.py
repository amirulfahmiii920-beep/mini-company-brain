"""Database connection and schema setup."""

from importlib.resources import files

import psycopg
from pgvector.psycopg import register_vector

from mini_company_brain.config import Settings


def connect(settings: Settings) -> psycopg.Connection:
    """Open an autocommit connection that can send and receive pgvector values.

    Autocommit means every statement commits on its own unless it runs inside an
    explicit `with conn.transaction():` block. Writes that must succeed or fail
    together use such a block; nothing is ever left open and uncommitted.
    """
    conn = psycopg.connect(settings.database_url, autocommit=True)
    # register_vector looks up the `vector` type, so the extension must exist
    # first. On a fresh database that means creating it here, before the schema.
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn


def apply_schema(conn: psycopg.Connection) -> None:
    """Create the tables if they do not exist. Safe to run many times."""
    schema_sql = files("mini_company_brain").joinpath("schema.sql").read_text(encoding="utf-8")
    with conn.transaction():
        conn.execute(schema_sql)
