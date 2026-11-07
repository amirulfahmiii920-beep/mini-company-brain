"""Command-line entry points."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

import psycopg

from mini_company_brain.config import PROJECT_ROOT, ConfigError, load_settings
from mini_company_brain.db import DatabaseConnectionError, apply_schema, connect
from mini_company_brain.documents import FrontMatterError
from mini_company_brain.embedding import FastEmbedEmbedder
from mini_company_brain.search import ACCESS_BY_ROLE, MAX_K, search
from mini_company_brain.store import ingest_folder

DEFAULT_DOCS_DIR = PROJECT_ROOT / "data" / "docs"
PREVIEW_CHARS = 200


def ingest_main(argv: Sequence[str] | None = None) -> int:
    """mcb-ingest: sync data/docs into Postgres. Returns the process exit code."""
    parser = argparse.ArgumentParser(
        prog="mcb-ingest", description="Load, chunk and embed the docs folder into Postgres."
    )
    parser.add_argument("--docs-dir", type=Path, default=DEFAULT_DOCS_DIR)
    args = parser.parse_args(argv)

    try:
        settings = load_settings()
        with connect(settings) as conn:
            apply_schema(conn)
            report = ingest_folder(conn, args.docs_dir, FastEmbedEmbedder(settings.model_cache_dir))
            total_chunks = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    # Expected failures get one clear line instead of a traceback. None of these
    # messages contain the password: ConfigError names variables only, and
    # DatabaseConnectionError is built without the connection string.
    except (
        ConfigError,
        DatabaseConnectionError,
        FrontMatterError,
        NotADirectoryError,
        ValueError,
    ) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    # Connected, but Postgres went away mid-run (for example Docker stopped).
    except psycopg.OperationalError as exc:
        print(f"Error: lost the connection to Postgres ({exc})", file=sys.stderr)
        return 1

    print(f"added:     {len(report.added)}")
    print(f"updated:   {len(report.updated)}")
    print(f"unchanged: {len(report.unchanged)}")
    print(f"removed:   {len(report.removed)}")
    for path in report.added + report.updated + report.removed:
        print(f"  {path}")
    print(f"chunks written this run: {report.chunks_written}")
    print(f"chunks in database:      {total_chunks}")
    return 0


def search_main(argv: Sequence[str] | None = None) -> int:
    """mcb-search: show the chunks closest to a question for a given role.

    A developer tool: --role is trusted as given. In the real app the role will
    come from the user's token and the database, never from the caller.
    """
    parser = argparse.ArgumentParser(
        prog="mcb-search", description="Search the ingested chunks as a given role."
    )
    parser.add_argument("query")
    # Default is the least-privileged role, so HR-only chunks never show by accident.
    parser.add_argument("--role", choices=sorted(ACCESS_BY_ROLE), default="employee")
    parser.add_argument("--k", type=int, default=5, help=f"number of results, 1 to {MAX_K}")
    args = parser.parse_args(argv)

    # Checked here as well as in search(), so a bad input fails before connecting.
    if not args.query.strip():
        print("Error: query must not be empty", file=sys.stderr)
        return 1
    print(f"role: {args.role}, top {args.k}")

    try:
        settings = load_settings()
        with connect(settings) as conn:
            embedder = FastEmbedEmbedder(settings.model_cache_dir)
            hits = search(conn, embedder, args.query, role=args.role, k=args.k)
    except (ConfigError, DatabaseConnectionError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except psycopg.OperationalError as exc:
        print(f"Error: lost the connection to Postgres ({exc})", file=sys.stderr)
        return 1

    if not hits:
        print("No chunks found. Has mcb-ingest been run?")
    for rank, hit in enumerate(hits, start=1):
        preview = " ".join(hit.content.split())[:PREVIEW_CHARS]
        print(f"\n{rank}. score {hit.score:.3f}  [{hit.access}]  {hit.source_path}")
        print(f"   {hit.heading}")
        print(f"   {preview}")
    return 0
