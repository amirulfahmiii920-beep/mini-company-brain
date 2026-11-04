"""Tests for the documents and chunks tables. Need the Docker Postgres."""

import psycopg
import pytest

from mini_company_brain.db import apply_schema

pytestmark = pytest.mark.integration

INSERT_DOCUMENT = (
    "INSERT INTO documents (source_path, title, doc_date, doc_type, access, content_hash) "
    "VALUES (%s, 'X', '2026-01-01', 'policy', %s, 'h') RETURNING id"
)


def test_schema_creates_tables_with_vector_384(db_conn):
    dim = db_conn.execute(
        "SELECT atttypmod FROM pg_attribute "
        "WHERE attrelid = 'chunks'::regclass AND attname = 'embedding'"
    ).fetchone()[0]
    assert dim == 384


def test_schema_is_idempotent(db_conn):
    apply_schema(db_conn)  # second run must not raise


def test_access_check_rejects_unknown_label(db_conn):
    with pytest.raises(psycopg.errors.CheckViolation):
        db_conn.execute(INSERT_DOCUMENT, ("x.md", "public"))


def test_chunk_access_check_rejects_unknown_label(db_conn):
    doc_id = db_conn.execute(INSERT_DOCUMENT, ("x.md", "all")).fetchone()[0]
    with pytest.raises(psycopg.errors.CheckViolation):
        db_conn.execute(
            "INSERT INTO chunks (document_id, chunk_index, heading, content, access, embedding) "
            "VALUES (%s, 0, 'H', 'text', 'HR', %s)",
            (doc_id, "[" + ",".join(["0"] * 384) + "]"),
        )


def test_deleting_document_deletes_its_chunks(db_conn):
    doc_id = db_conn.execute(INSERT_DOCUMENT, ("x.md", "all")).fetchone()[0]
    db_conn.execute(
        "INSERT INTO chunks (document_id, chunk_index, heading, content, access, embedding) "
        "VALUES (%s, 0, 'H', 'text', 'all', %s)",
        (doc_id, "[" + ",".join(["0"] * 384) + "]"),
    )
    db_conn.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
    assert db_conn.execute("SELECT count(*) FROM chunks").fetchone()[0] == 0
