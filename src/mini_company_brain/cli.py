"""Command-line entry points."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

import psycopg

from mini_company_brain.config import PROJECT_ROOT, ConfigError, load_settings
from mini_company_brain.db import apply_schema, connect
from mini_company_brain.documents import FrontMatterError
from mini_company_brain.embedding import FastEmbedEmbedder
from mini_company_brain.store import ingest_folder

DEFAULT_DOCS_DIR = PROJECT_ROOT / "data" / "docs"


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
    # psycopg errors describe the server, not the connection string.
    except (ConfigError, FrontMatterError, NotADirectoryError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except psycopg.OperationalError as exc:
        print(f"Error: cannot reach Postgres. Is Docker running? ({exc})", file=sys.stderr)
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
