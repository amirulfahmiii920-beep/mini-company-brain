"""Tests for saving documents and chunks. Need the Docker Postgres; use FakeEmbedder."""

from pathlib import Path

import pytest

from mini_company_brain.documents import FrontMatterError
from mini_company_brain.store import ingest_folder

pytestmark = pytest.mark.integration

DOCS_DIR = Path(__file__).resolve().parents[2] / "data" / "docs"
HR_FILES = {
    "2026-09-30-performance-review-danial.md",
    "2026-10-06-disciplinary-jason-lim.md",
    "2026-10-15-salary-bands-2026.md",
}


def doc_text(access: str = "all", extra: str = "") -> str:
    return (
        f"---\ntitle: Test\ndate: 2026-01-01\ntype: policy\naccess: {access}\n---\n\n"
        f"# Test\n\n## A\n\nalpha text {extra}\n\n## B\n\nbeta text\n"
    )


def count(conn, table: str) -> int:
    return conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]


def test_ingest_saves_all_docs_with_metadata(db_conn, fake_embedder):
    report = ingest_folder(db_conn, DOCS_DIR, fake_embedder)
    assert len(report.added) == 26
    assert count(db_conn, "documents") == 26
    assert count(db_conn, "chunks") == report.chunks_written == 164
    row = db_conn.execute(
        "SELECT d.source_path, c.heading, c.access FROM chunks c "
        "JOIN documents d ON d.id = c.document_id WHERE c.heading LIKE '%%2.1 Entitlement'"
    ).fetchone()
    assert row == (
        "policy-hr-002-leave.md",
        "HR-POL-002 Leave Policy > 2. Annual leave > 2.1 Entitlement",
        "all",
    )


def test_hr_docs_chunks_are_labelled_hr(db_conn, fake_embedder):
    ingest_folder(db_conn, DOCS_DIR, fake_embedder)
    rows = db_conn.execute(
        "SELECT DISTINCT d.source_path FROM chunks c "
        "JOIN documents d ON d.id = c.document_id WHERE c.access = 'hr'"
    ).fetchall()
    assert {r[0] for r in rows} == HR_FILES


def test_second_run_is_idempotent(db_conn, fake_embedder):
    ingest_folder(db_conn, DOCS_DIR, fake_embedder)
    before = count(db_conn, "chunks")
    report = ingest_folder(db_conn, DOCS_DIR, fake_embedder)
    assert len(report.unchanged) == 26
    assert report.added == report.updated == report.removed == []
    assert report.chunks_written == 0
    assert count(db_conn, "chunks") == before


def test_access_change_updates_chunks(db_conn, fake_embedder, tmp_path):
    (tmp_path / "a.md").write_text(doc_text("all"), encoding="utf-8")
    ingest_folder(db_conn, tmp_path, fake_embedder)
    (tmp_path / "a.md").write_text(doc_text("hr"), encoding="utf-8")

    report = ingest_folder(db_conn, tmp_path, fake_embedder)

    assert report.updated == ["a.md"]
    assert db_conn.execute("SELECT access FROM documents").fetchall() == [("hr",)]
    assert {r[0] for r in db_conn.execute("SELECT access FROM chunks").fetchall()} == {"hr"}


def test_edited_doc_replaces_old_chunks(db_conn, fake_embedder, tmp_path):
    (tmp_path / "a.md").write_text(doc_text(extra="old"), encoding="utf-8")
    ingest_folder(db_conn, tmp_path, fake_embedder)
    (tmp_path / "a.md").write_text(doc_text(extra="new"), encoding="utf-8")
    ingest_folder(db_conn, tmp_path, fake_embedder)
    contents = [r[0] for r in db_conn.execute("SELECT content FROM chunks").fetchall()]
    assert len(contents) == 2
    assert any("new" in c for c in contents) and not any("old" in c for c in contents)


def test_bad_file_aborts_before_any_write(db_conn, fake_embedder, tmp_path):
    (tmp_path / "a.md").write_text(doc_text("all"), encoding="utf-8")
    (tmp_path / "b.md").write_text(doc_text("HR"), encoding="utf-8")
    with pytest.raises(FrontMatterError, match=r"^b\.md"):
        ingest_folder(db_conn, tmp_path, fake_embedder)
    assert count(db_conn, "documents") == 0


def test_removed_file_is_removed_from_db(db_conn, fake_embedder, tmp_path):
    (tmp_path / "a.md").write_text(doc_text("all"), encoding="utf-8")
    (tmp_path / "b.md").write_text(doc_text("hr"), encoding="utf-8")
    ingest_folder(db_conn, tmp_path, fake_embedder)
    (tmp_path / "b.md").unlink()

    report = ingest_folder(db_conn, tmp_path, fake_embedder)

    assert report.removed == ["b.md"]
    assert db_conn.execute("SELECT source_path FROM documents").fetchall() == [("a.md",)]
    assert count(db_conn, "chunks") == 2
    assert db_conn.execute("SELECT count(*) FROM chunks WHERE access = 'hr'").fetchone()[0] == 0


def test_embeddings_are_stored_for_every_chunk(db_conn, fake_embedder, tmp_path):
    (tmp_path / "a.md").write_text(doc_text(), encoding="utf-8")
    ingest_folder(db_conn, tmp_path, fake_embedder)
    dims = db_conn.execute("SELECT vector_dims(embedding) FROM chunks").fetchall()
    assert dims == [(384,), (384,)]
