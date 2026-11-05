"""Tests for splitting a document into heading-based chunks."""

from datetime import date
from pathlib import Path

from mini_company_brain.chunking import MAX_CHUNK_WORDS, chunk_document
from mini_company_brain.documents import Document, load_document, load_folder

DOCS_DIR = Path(__file__).resolve().parents[2] / "data" / "docs"


def make_doc(body: str, access: str = "all", source_path: str = "x.md") -> Document:
    return Document(
        source_path=source_path,
        title="Test Doc",
        date=date(2026, 1, 1),
        doc_type="policy",
        access=access,
        body=body,
        content_hash="h",
    )


def words(n: int, word: str = "word") -> str:
    return " ".join([word] * n)


def test_heading_path_for_nested_section():
    chunks = chunk_document(load_document(DOCS_DIR / "policy-hr-002-leave.md", DOCS_DIR))
    entitlement = next(c for c in chunks if c.heading.endswith("2.1 Entitlement"))
    assert entitlement.heading == "HR-POL-002 Leave Policy > 2. Annual leave > 2.1 Entitlement"
    assert "14 days" in entitlement.content


def test_sibling_heading_replaces_previous_one():
    body = "# T\n\n## A\n\n### A1\n\na1 text\n\n## B\n\nb text\n"
    headings = [c.heading for c in chunk_document(make_doc(body))]
    assert headings == ["T > A > A1", "T > B"]


def test_empty_parent_section_is_dropped():
    chunks = chunk_document(load_document(DOCS_DIR / "policy-hr-002-leave.md", DOCS_DIR))
    assert not any(c.heading.endswith("2. Annual leave") for c in chunks)


def test_text_under_h1_is_kept():
    doc = load_document(DOCS_DIR / "2026-09-01-brief-rakanpay-v2.md", DOCS_DIR)
    first = chunk_document(doc)[0]
    assert first.heading == "Project Brief: RakanPay v2"
    assert "Project owner: Priya Nair" in first.content


def test_text_before_any_heading_uses_document_title():
    chunks = chunk_document(make_doc("Intro line.\n\n# H\n\nBody.\n"))
    assert (chunks[0].heading, chunks[0].content) == ("Test Doc", "Intro line.")


def test_heading_line_is_not_repeated_in_content():
    chunks = chunk_document(make_doc("# T\n\n## A\n\nonly body\n"))
    assert chunks[0].content == "only body"


def test_every_chunk_carries_source_and_access():
    doc = make_doc("# T\n\n## A\n\na\n\n## B\n\nb\n", access="hr", source_path="secret.md")
    chunks = chunk_document(doc)
    assert len(chunks) == 2
    assert all((c.source_path, c.access) == ("secret.md", "hr") for c in chunks)


def test_chunk_index_counts_from_zero_across_document():
    body = "# T\n\n## A\n\na\n\n## B\n\nb\n\n## C\n\nc\n"
    assert [c.chunk_index for c in chunk_document(make_doc(body))] == [0, 1, 2]


def test_long_section_is_split_at_paragraphs():
    body = "# T\n\n## S\n\n" + "\n\n".join(words(200, w) for w in ["alpha", "beta", "gamma"])
    chunks = chunk_document(make_doc(body))
    assert [c.heading for c in chunks] == ["T > S"] * 3
    assert [c.content.split()[0] for c in chunks] == ["alpha", "beta", "gamma"]


def test_small_paragraphs_are_packed_together():
    paragraphs = [words(100, w) for w in ["alpha", "beta", "gamma", "delta"]]
    body = "# T\n\n## S\n\n" + "\n\n".join(paragraphs)
    chunks = chunk_document(make_doc(body))
    assert [len(c.content.split()) for c in chunks] == [300, 100]


def test_oversized_single_paragraph_stays_whole():
    chunks = chunk_document(make_doc("# T\n\n## S\n\n" + words(400)))
    assert len(chunks) == 1
    assert len(chunks[0].content.split()) == 400


def test_embedding_text_includes_title_and_heading():
    chunk = chunk_document(make_doc("# T\n\n## A\n\nbody\n"))[0]
    assert chunk.embedding_text("Test Doc") == "Test Doc\nT > A\n\nbody"


def test_real_docs_chunk_within_limit():
    for doc in load_folder(DOCS_DIR):
        chunks = chunk_document(doc)
        assert chunks, doc.source_path
        for c in chunks:
            assert c.content.strip(), (doc.source_path, c.heading)
            assert len(c.content.split()) <= MAX_CHUNK_WORDS or "\n\n" not in c.content
