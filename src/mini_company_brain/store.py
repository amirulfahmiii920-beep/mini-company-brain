"""Save documents and their embedded chunks, keeping the database in sync with the folder."""

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import psycopg

from mini_company_brain.chunking import Chunk, chunk_document
from mini_company_brain.documents import Document, load_folder
from mini_company_brain.embedding import Embedder


@dataclass
class IngestReport:
    added: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    chunks_written: int = 0


def save_document(
    conn: psycopg.Connection,
    doc: Document,
    chunks: list[Chunk],
    embeddings: list[np.ndarray],
) -> None:
    """Insert or replace one document and all of its chunks, in one transaction.

    If anything fails, the document keeps its previous rows; it is never left
    half-written.
    """
    if len(chunks) != len(embeddings):
        raise ValueError(
            f"{doc.source_path}: {len(chunks)} chunks but {len(embeddings)} embeddings"
        )
    with conn.transaction():
        document_id = conn.execute(
            """
            INSERT INTO documents (source_path, title, doc_date, doc_type, access, content_hash)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (source_path) DO UPDATE SET
                title = EXCLUDED.title,
                doc_date = EXCLUDED.doc_date,
                doc_type = EXCLUDED.doc_type,
                access = EXCLUDED.access,
                content_hash = EXCLUDED.content_hash,
                ingested_at = now()
            RETURNING id
            """,
            (doc.source_path, doc.title, doc.date, doc.doc_type, doc.access, doc.content_hash),
        ).fetchone()[0]

        # Replacing every chunk is simpler than diffing sections, and it is what
        # keeps chunks.access equal to documents.access after a label change.
        conn.execute("DELETE FROM chunks WHERE document_id = %s", (document_id,))
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO chunks (document_id, chunk_index, heading, content, access, embedding)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [
                    (document_id, c.chunk_index, c.heading, c.content, doc.access, vector)
                    for c, vector in zip(chunks, embeddings, strict=True)
                ],
            )


def ingest_folder(conn: psycopg.Connection, docs_dir: Path, embedder: Embedder) -> IngestReport:
    """Make the database match docs_dir: add new files, update changed ones, remove gone ones.

    Every file is read, validated and chunked before anything is written, so one
    bad file stops the run with the database untouched.
    """
    documents = load_folder(docs_dir)
    chunks_by_path = {doc.source_path: chunk_document(doc) for doc in documents}

    stored_hashes = dict(conn.execute("SELECT source_path, content_hash FROM documents").fetchall())
    report = IngestReport()

    for doc in documents:
        stored_hash = stored_hashes.get(doc.source_path)
        if stored_hash == doc.content_hash:
            report.unchanged.append(doc.source_path)
            continue
        chunks = chunks_by_path[doc.source_path]
        embeddings = embedder.embed_passages([c.embedding_text(doc.title) for c in chunks])
        save_document(conn, doc, chunks, embeddings)
        (report.added if stored_hash is None else report.updated).append(doc.source_path)
        report.chunks_written += len(chunks)

    report.removed = sorted(set(stored_hashes) - set(chunks_by_path))
    if report.removed:
        # ON DELETE CASCADE removes their chunks too, so they stop being searchable.
        conn.execute("DELETE FROM documents WHERE source_path = ANY(%s)", (report.removed,))
    return report
