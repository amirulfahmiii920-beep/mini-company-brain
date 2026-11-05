"""Role-filtered vector search over the stored chunks."""

from dataclasses import dataclass
from typing import Literal

import psycopg

from mini_company_brain.documents import Access
from mini_company_brain.embedding import Embedder

Role = Literal["employee", "hr"]

# Which access labels each role may read. In a later step the role comes from
# the users table (SPEC section 6); here it is passed in by the caller.
ACCESS_BY_ROLE: dict[str, tuple[Access, ...]] = {
    "employee": ("all",),
    "hr": ("all", "hr"),
}
MAX_K = 50


@dataclass(frozen=True)
class SearchHit:
    source_path: str
    heading: str
    content: str
    access: Access
    score: float  # cosine similarity, 1 - cosine distance; higher is closer


def allowed_access(role: Role) -> tuple[Access, ...]:
    """Map a role to its readable labels. An unknown role raises (fail closed)."""
    try:
        return ACCESS_BY_ROLE[role]
    except (KeyError, TypeError):
        raise ValueError(f"Unknown role {role!r}. Expected one of: employee, hr") from None


# The access filter is in the WHERE clause, so rows the role may not read never
# leave Postgres. Filtering in Python after the query would fetch them first.
# No vector index exists, so this is an exact scan and always returns up to k
# rows that pass the filter.
SEARCH_SQL = """
    SELECT d.source_path, c.heading, c.content, c.access,
           1 - (c.embedding <=> %(query)s) AS score
    FROM chunks c
    JOIN documents d ON d.id = c.document_id
    WHERE c.access = ANY(%(allowed)s)
    ORDER BY c.embedding <=> %(query)s
    LIMIT %(k)s
"""


def search(
    conn: psycopg.Connection,
    embedder: Embedder,
    query: str,
    role: Role,
    k: int = 5,
) -> list[SearchHit]:
    """Return the k chunks closest in meaning to query that role may read, best first."""
    # All input checks run before the model or the database is touched.
    if not query or not query.strip():
        raise ValueError("query must not be empty")
    if not 1 <= k <= MAX_K:
        raise ValueError(f"k must be between 1 and {MAX_K}, got {k}")
    allowed = allowed_access(role)

    query_vector = embedder.embed_query(query.strip())
    # The query text never goes into the SQL string: only its vector is sent, as
    # a bound parameter.
    rows = conn.execute(
        SEARCH_SQL, {"query": query_vector, "allowed": list(allowed), "k": k}
    ).fetchall()
    return [
        SearchHit(source_path=r[0], heading=r[1], content=r[2], access=r[3], score=float(r[4]))
        for r in rows
    ]
