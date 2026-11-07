"""Database connection and schema setup."""

from importlib.resources import files

import psycopg
from pgvector.psycopg import register_vector
from psycopg.conninfo import conninfo_to_dict

from mini_company_brain.config import Settings


class DatabaseConnectionError(RuntimeError):
    """Postgres could not be reached. The message never contains the connection string."""


def _safe_reason(exc: psycopg.OperationalError, database_url: str) -> str:
    """libpq's one-line reason (for example "Connection refused"), password removed.

    libpq describes the server, not the connection string, so the password should
    never be in it; replacing it anyway keeps that a guarantee, not an assumption.
    This lives in its own function so the password is never a local variable of a
    frame that is still in the traceback (pytest can print locals).
    """
    reason = " ".join(str(exc).split()) or type(exc).__name__
    password = conninfo_to_dict(database_url).get("password")
    if password:
        reason = reason.replace(str(password), "***")
    return reason


def connect(settings: Settings) -> psycopg.Connection:
    """Open an autocommit connection that can send and receive pgvector values.

    Autocommit means every statement commits on its own unless it runs inside an
    explicit `with conn.transaction():` block. Writes that must succeed or fail
    together use such a block; nothing is ever left open and uncommitted.

    Raises DatabaseConnectionError if Postgres cannot be reached.
    """
    try:
        conn = psycopg.connect(settings.database_url, autocommit=True)
    except psycopg.OperationalError as exc:
        # `from None` leaves the psycopg error out of the traceback. Its frames
        # hold the full connection string as an argument, and pytest prints frame
        # arguments when a test fails: that is how the real password leaked.
        raise DatabaseConnectionError(
            f"Cannot connect to Postgres ({_safe_reason(exc, settings.database_url)}). "
            "Is Docker running?"
        ) from None
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
