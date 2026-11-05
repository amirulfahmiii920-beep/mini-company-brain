"""Tests for reading a Markdown file and validating its front matter."""

from datetime import date
from pathlib import Path

import pytest

from mini_company_brain.documents import FrontMatterError, load_document, load_folder

DOCS_DIR = Path(__file__).resolve().parents[2] / "data" / "docs"

VALID = """---
title: "Leave Policy"
date: 2026-09-01
type: policy
access: all
---

# Leave Policy

Body text.
"""


def write(folder: Path, name: str, text: str) -> Path:
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


def test_loads_valid_front_matter(tmp_path):
    doc = load_document(write(tmp_path, "a.md", VALID), tmp_path)
    assert (doc.source_path, doc.title, doc.doc_type, doc.access) == (
        "a.md",
        "Leave Policy",
        "policy",
        "all",
    )
    assert doc.date == date(2026, 9, 1)


def test_body_excludes_front_matter(tmp_path):
    doc = load_document(write(tmp_path, "a.md", VALID), tmp_path)
    assert doc.body.lstrip().startswith("# Leave Policy")
    assert "access:" not in doc.body


def test_content_hash_changes_when_file_changes(tmp_path):
    first = load_document(write(tmp_path, "a.md", VALID), tmp_path).content_hash
    second = load_document(write(tmp_path, "a.md", VALID + "More.\n"), tmp_path).content_hash
    assert first != second


@pytest.mark.parametrize("bad", ["HR", "Hr", "public", "''"])
def test_rejects_unknown_access_label(tmp_path, bad):
    text = VALID.replace("access: all", f"access: {bad}")
    with pytest.raises(FrontMatterError, match=r"^a\.md"):
        load_document(write(tmp_path, "a.md", text), tmp_path)


@pytest.mark.parametrize("key", ["title", "date", "type", "access"])
def test_rejects_missing_key(tmp_path, key):
    text = "\n".join(line for line in VALID.splitlines() if not line.startswith(f"{key}:"))
    with pytest.raises(FrontMatterError, match=key):
        load_document(write(tmp_path, "a.md", text), tmp_path)


def test_rejects_date_that_is_not_a_date(tmp_path):
    text = VALID.replace("date: 2026-09-01", 'date: "soon"')
    with pytest.raises(FrontMatterError, match="date"):
        load_document(write(tmp_path, "a.md", text), tmp_path)


def test_rejects_missing_front_matter(tmp_path):
    with pytest.raises(FrontMatterError, match=r"^a\.md"):
        load_document(write(tmp_path, "a.md", "# Just a heading\n"), tmp_path)


def test_rejects_unclosed_front_matter(tmp_path):
    with pytest.raises(FrontMatterError, match=r"^a\.md"):
        load_document(write(tmp_path, "a.md", "---\ntitle: X\naccess: all\n"), tmp_path)


def test_rejects_yaml_that_builds_python_objects(tmp_path):
    # yaml.load would build this object; yaml.safe_load refuses the tag.
    text = VALID.replace('title: "Leave Policy"', "title: !!python/object/apply:os.getcwd []")
    with pytest.raises(FrontMatterError, match=r"^a\.md"):
        load_document(write(tmp_path, "a.md", text), tmp_path)


def test_body_horizontal_rule_is_not_front_matter_end(tmp_path):
    doc = load_document(write(tmp_path, "a.md", VALID + "\nbefore\n---\nafter\n"), tmp_path)
    assert "before\n---\nafter" in doc.body


def test_reads_utf8(tmp_path):
    doc = load_document(write(tmp_path, "a.md", VALID + "café · RM8,000\n"), tmp_path)
    assert "café · RM8,000" in doc.body


def test_load_folder_on_real_docs():
    docs = load_folder(DOCS_DIR)
    assert len(docs) == 26
    assert sorted(d.source_path for d in docs if d.access == "hr") == [
        "2026-09-30-performance-review-danial.md",
        "2026-10-06-disciplinary-jason-lim.md",
        "2026-10-15-salary-bands-2026.md",
    ]


def test_load_folder_rejects_missing_folder(tmp_path):
    # A typo in --docs-dir must not look like "every file was removed".
    with pytest.raises(NotADirectoryError):
        load_folder(tmp_path / "does-not-exist")


def test_load_folder_rejects_folder_without_markdown(tmp_path):
    write(tmp_path, "notes.txt", "not markdown")
    with pytest.raises(ValueError, match="no .md files"):
        load_folder(tmp_path)


def test_load_folder_stops_on_first_bad_file(tmp_path):
    write(tmp_path, "a.md", VALID)
    write(tmp_path, "b.md", VALID.replace("access: all", "access: HR"))
    with pytest.raises(FrontMatterError, match=r"^b\.md"):
        load_folder(tmp_path)
