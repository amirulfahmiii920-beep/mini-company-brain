"""Read Markdown documents and validate their YAML front matter."""

import hashlib
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Literal, get_args

import yaml

Access = Literal["all", "hr"]
ACCESS_LABELS: tuple[str, ...] = get_args(Access)

FRONT_MATTER_FENCE = "---"


class FrontMatterError(ValueError):
    """A document's front matter is missing or invalid. The message starts with the file name."""


@dataclass(frozen=True)
class Document:
    source_path: str  # relative to the docs folder, with forward slashes
    title: str
    date: date
    doc_type: str
    access: Access
    body: str  # everything after the front matter
    content_hash: str  # sha256 of the normalised text, used to skip unchanged files


def load_document(path: Path, docs_dir: Path) -> Document:
    """Read one Markdown file. Raises FrontMatterError if it cannot be trusted."""
    source_path = path.relative_to(docs_dir).as_posix()

    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FrontMatterError(f"{source_path}: file is not valid UTF-8") from exc
    # Git on Windows may check files out with CRLF. Normalising keeps the hash
    # and the chunks identical on every machine.
    text = text.replace("\r\n", "\n")

    front_matter, body = _split_front_matter(source_path, text)
    meta = _parse_front_matter(source_path, front_matter)

    return Document(
        source_path=source_path,
        title=meta["title"],
        date=meta["date"],
        doc_type=meta["type"],
        access=meta["access"],
        body=body,
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )


def load_folder(docs_dir: Path) -> list[Document]:
    """Load every *.md file in docs_dir, sorted by name.

    Raises on the first invalid file, so a caller can validate the whole folder
    before writing anything to the database.
    """
    if not docs_dir.is_dir():
        raise NotADirectoryError(f"Docs folder not found: {docs_dir}")
    paths = sorted(docs_dir.glob("*.md"))
    if not paths:
        # An empty result would make every stored document look removed.
        raise ValueError(f"Docs folder has no .md files: {docs_dir}")
    return [load_document(path, docs_dir) for path in paths]


def _split_front_matter(source_path: str, text: str) -> tuple[str, str]:
    lines = text.split("\n")
    if lines[0].rstrip() != FRONT_MATTER_FENCE:
        raise FrontMatterError(f"{source_path}: file must start with a '---' front matter block")
    # The front matter ends at the first line that is exactly '---'. Later '---'
    # lines (horizontal rules) belong to the body.
    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip() == FRONT_MATTER_FENCE:
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1 :])
    raise FrontMatterError(f"{source_path}: front matter has no closing '---' line")


def _parse_front_matter(source_path: str, front_matter: str) -> dict:
    try:
        # safe_load only builds plain types (str, int, date, list, dict). yaml.load
        # would let a file construct arbitrary Python objects.
        meta = yaml.safe_load(front_matter)
    except yaml.YAMLError as exc:
        raise FrontMatterError(f"{source_path}: front matter is not valid YAML ({exc})") from exc
    if not isinstance(meta, dict):
        raise FrontMatterError(f"{source_path}: front matter must be a YAML mapping")

    for key in ("title", "type"):
        value = meta.get(key)
        if not isinstance(value, str) or not value.strip():
            raise FrontMatterError(f"{source_path}: '{key}' must be a non-empty string")

    doc_date = meta.get("date")
    # datetime is a subclass of date, so it is excluded explicitly.
    if not isinstance(doc_date, date) or isinstance(doc_date, datetime):
        raise FrontMatterError(f"{source_path}: 'date' must be a date like 2026-09-01")

    # Fail closed: only the exact labels are accepted, never a default.
    if meta.get("access") not in ACCESS_LABELS:
        raise FrontMatterError(
            f"{source_path}: 'access' must be one of {', '.join(ACCESS_LABELS)}, "
            f"got {meta.get('access')!r}"
        )
    return meta
