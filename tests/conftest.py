"""Shared pytest fixtures."""

import hashlib
import secrets
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import psycopg
import pytest

from mini_company_brain.config import load_settings
from mini_company_brain.db import apply_schema, connect
from mini_company_brain.embedding import EMBEDDING_DIM, FastEmbedEmbedder
from mini_company_brain.store import ingest_folder

DOCS_DIR = Path(__file__).resolve().parents[1] / "data" / "docs"


class FakeEmbedder:
    """Deterministic stand-in for the real model: the same text always gives the same
    unit vector. Lets store tests run without downloading anything."""

    def _vector(self, text: str) -> np.ndarray:
        seed = int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")
        vector = np.random.default_rng(seed).standard_normal(EMBEDDING_DIM).astype(np.float32)
        return vector / np.linalg.norm(vector)

    def embed_passages(self, texts: list[str]) -> list[np.ndarray]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> np.ndarray:
        return self._vector(text)


@pytest.fixture
def fake_embedder() -> FakeEmbedder:
    return FakeEmbedder()


@contextmanager
def temp_schema_connection() -> Iterator[psycopg.Connection]:
    """A connection whose tables live in a throwaway schema named test_<random>.

    Tests never read or change real ingested data. The vector extension stays in
    `public`, which is why `public` is kept on the search_path.
    """
    schema = f"test_{secrets.token_hex(4)}"
    conn = connect(load_settings())
    try:
        conn.execute(f"CREATE SCHEMA {schema}")
        conn.execute(f"SET search_path TO {schema}, public")
        apply_schema(conn)
        yield conn
    finally:
        conn.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
        conn.close()


@pytest.fixture
def db_conn() -> Iterator[psycopg.Connection]:
    """A fresh throwaway schema for each test."""
    with temp_schema_connection() as conn:
        yield conn


@pytest.fixture(scope="session")
def embedder() -> FastEmbedEmbedder:
    """The real local model (from .cache/fastembed). Loaded once per test run."""
    return FastEmbedEmbedder(load_settings().model_cache_dir)


@pytest.fixture(scope="session")
def search_db(embedder) -> Iterator[psycopg.Connection]:
    """The 26 real docs, ingested once with the real model into a throwaway schema.

    Read-only for tests: a test that wrote here would affect every later test.
    """
    with temp_schema_connection() as conn:
        ingest_folder(conn, DOCS_DIR, embedder)
        yield conn
