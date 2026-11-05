"""Split a document into chunks, one per Markdown section."""

import re
from dataclasses import dataclass

from mini_company_brain.documents import Access, Document

# About 400 tokens once the title and heading are added, which stays under the
# 512-token limit of BAAI/bge-small-en-v1.5. Text past that limit would be cut
# off silently by the model.
MAX_CHUNK_WORDS = 300

HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")
PARAGRAPH_BREAK = re.compile(r"\n\s*\n")
HEADING_SEPARATOR = " > "


@dataclass(frozen=True)
class Chunk:
    source_path: str
    chunk_index: int
    heading: str  # full path, e.g. "HR-POL-002 Leave Policy > 2. Annual leave > 2.1 Entitlement"
    content: str
    access: Access

    def embedding_text(self, title: str) -> str:
        """Text sent to the embedding model. Title and heading help short sections match."""
        return f"{title}\n{self.heading}\n\n{self.content}"


def chunk_document(doc: Document) -> list[Chunk]:
    """Split doc.body by heading, then split long sections at paragraph breaks.

    Known limitation: a '#' line inside a fenced code block would be read as a
    heading. None of the current documents contain code blocks.
    """
    contents_by_heading = [
        (heading, part)
        for heading, section in _sections(doc)
        for part in _split_long_section(section)
    ]
    return [
        Chunk(
            source_path=doc.source_path,
            chunk_index=index,
            heading=heading,
            content=content,
            access=doc.access,
        )
        for index, (heading, content) in enumerate(contents_by_heading)
    ]


def _sections(doc: Document) -> list[tuple[str, str]]:
    """Return (heading path, content) for every section that has text."""
    sections: list[tuple[str, str]] = []
    stack: list[tuple[int, str]] = []  # (level, heading text) from H1 down
    heading = doc.title  # used for text before the first heading
    lines: list[str] = []

    def flush() -> None:
        content = "\n".join(lines).strip()
        if content:  # a heading followed directly by a sub-heading has no text
            sections.append((heading, content))

    for line in doc.body.split("\n"):
        match = HEADING_PATTERN.match(line)
        if not match:
            lines.append(line)
            continue
        flush()
        level, text = len(match.group(1)), match.group(2).strip()
        # Leave the parents of this heading on the stack; drop siblings and deeper ones.
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, text))
        heading = HEADING_SEPARATOR.join(text for _, text in stack)
        lines = []
    flush()
    return sections


def _split_long_section(content: str) -> list[str]:
    """Pack paragraphs into parts of at most MAX_CHUNK_WORDS words.

    A single paragraph longer than the limit (for example a big table) is kept
    whole, because cutting it mid-row would break its meaning.
    """
    if len(content.split()) <= MAX_CHUNK_WORDS:
        return [content]

    parts: list[str] = []
    current: list[str] = []
    current_words = 0
    for paragraph in PARAGRAPH_BREAK.split(content):
        paragraph_words = len(paragraph.split())
        if current and current_words + paragraph_words > MAX_CHUNK_WORDS:
            parts.append("\n\n".join(current))
            current, current_words = [], 0
        current.append(paragraph)
        current_words += paragraph_words
    if current:
        parts.append("\n\n".join(current))
    return parts
