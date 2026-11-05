"""Shared pytest fixtures."""

import hashlib
import secrets
from collections.abc import Iterator

import numpy as np
import psycopg
import pytest

from mini_company_brain.config import load_settings
from mini_company_brain.db import apply_schema, connect
from mini_company_brain.embedding import EMBEDDING_DIM


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


@pytest.fixture
def db_conn() -> Iterator[psycopg.Connection]:
    """A connection whose tables live in a throwaway schema.

    Each test gets its own schema named test_<random>, so tests never read or
    change real ingested data. The vector extension stays in `public`, which is
    why `public` is kept on the search_path.
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
