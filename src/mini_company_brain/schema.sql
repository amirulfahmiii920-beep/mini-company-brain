-- Tables for ingested documents and their embedded chunks.
-- Every statement is idempotent, so apply_schema() can run on every ingest.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_path  TEXT NOT NULL UNIQUE,        -- file name relative to data/docs/
    title        TEXT NOT NULL,
    doc_date     DATE NOT NULL,
    doc_type     TEXT NOT NULL,
    access       TEXT NOT NULL CHECK (access IN ('all', 'hr')),
    content_hash TEXT NOT NULL,               -- sha256 of the file, to skip unchanged files
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- access is copied from documents on purpose: the search filter stays on one
-- table, and a later Row-Level Security policy can check each row without a join.
-- Both copies are always written in the same transaction.
-- No vector index yet: about 150 rows, so an exact scan is fast and always
-- returns k rows even with an access filter.
CREATE TABLE IF NOT EXISTS chunks (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    heading     TEXT NOT NULL,
    content     TEXT NOT NULL,
    access      TEXT NOT NULL CHECK (access IN ('all', 'hr')),
    embedding   vector(384) NOT NULL,         -- BAAI/bge-small-en-v1.5 output size
    UNIQUE (document_id, chunk_index)
);
