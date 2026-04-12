"""
database.py
-----------
Database connection and schema bootstrap.

Supports two backends selected automatically at startup:
  • LOCAL  (no DATABASE_URL)  → SQLite via DATABASE_PATH
  • RENDER (DATABASE_URL set) → PostgreSQL via psycopg (v3)

Public API — unchanged from the original SQLite version:
  get_db()   → returns a connection-like object (context manager, .execute())
  init_db()  → creates all tables if they don't exist (safe to call repeatedly)

All models continue to use:
    with get_db() as conn:
        conn.execute("...", (...))   # positional ? placeholders work on both backends
        conn.fetchone() / fetchall() # on the cursor returned by .execute()
"""

import os
import logging
import sqlite3
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from config import Config

logger = logging.getLogger(__name__)


# ── Engine factory ────────────────────────────────────────────────────────────

def _make_engine():
    """
    Build a SQLAlchemy engine.

    Decision logic:
      DATABASE_URL is set  →  PostgreSQL (Render production)
      DATABASE_URL not set →  SQLite    (local development)

    The engine is created once at module import time and reused for the
    lifetime of the process — safe under Gunicorn multi-worker because
    each worker is a separate process with its own engine.
    """
    db_url = os.getenv("DATABASE_URL", "")

    if db_url:
        # Render sets DATABASE_URL with the legacy "postgres://" scheme.
        # SQLAlchemy 1.4+ requires "postgresql://".
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif db_url.startswith("postgresql://") and "+psycopg" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

        logger.info("Database backend: PostgreSQL")
        return create_engine(
            db_url,
            pool_pre_ping=True,   # drop stale connections automatically
            pool_size=5,
            max_overflow=10,
        )
    else:
        sqlite_path = Config.DATABASE_PATH
        logger.info("Database backend: SQLite (%s)", sqlite_path)
        return create_engine(
            f"sqlite:///{sqlite_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,   # single connection; safe for dev/testing
        )


_engine = _make_engine()


# ── Parameter-style adapter ───────────────────────────────────────────────────
# SQLAlchemy's text() always uses :name style — never ? or %s.
# We convert positional ? placeholders → :p0, :p1, ... and turn the
# params tuple into a matching dict so both SQLite and PostgreSQL work.

def _adapt_sql(sql: str, params: tuple) -> tuple[str, dict]:
    """
    Convert ?-style positional SQL + params tuple into
    SQLAlchemy text()-compatible :p0/:p1/... style + dict.
    """
    param_dict = {}
    new_sql = sql
    for i, val in enumerate(params):
        key = f"p{i}"
        new_sql = new_sql.replace("?", f":{key}", 1)
        param_dict[key] = val
    return new_sql, param_dict


# ── Connection wrapper ────────────────────────────────────────────────────────

class _Connection:
    """
    Thin wrapper that makes a SQLAlchemy connection look like the
    sqlite3.Connection the models were written against.

    Supported interface:
        conn.execute(sql, params)  → cursor-like object with .fetchone() / .fetchall()
        conn.executescript(sql)    → runs multiple ; separated statements (init_db only)
        used as context manager    → commits on __exit__, rolls back on exception
    """

    def __init__(self, sa_conn):
        self._conn = sa_conn

    # ── context manager ───────────────────────────────────────────────────
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._conn.rollback()
        else:
            self._conn.commit()
        self._conn.close()
        return False   # never suppress exceptions

    # ── query helpers ─────────────────────────────────────────────────────
    def execute(self, sql: str, params=()):
        adapted_sql, param_dict = _adapt_sql(sql, params)
        result = self._conn.execute(text(adapted_sql), param_dict)
        return _Cursor(result)

    def executescript(self, sql: str):
        """
        Used only by init_db(). Splits on ';' and runs each statement.
        Strips SQL comments before splitting so empty fragments are skipped.
        """
        for statement in sql.split(";"):
            stmt = statement.strip()
            # Skip blank lines and pure-comment blocks
            lines = [l for l in stmt.splitlines() if l.strip() and not l.strip().startswith("--")]
            if not lines:
                continue
            clean = "\n".join(lines).strip()
            if clean:
                adapted_sql, _ = _adapt_sql(clean, ())
                self._conn.execute(text(adapted_sql))
        self._conn.commit()


class _Cursor:
    """
    Wraps a SQLAlchemy CursorResult to expose fetchone() / fetchall()
    that return dict-like row objects — matching sqlite3.Row behaviour.
    """

    def __init__(self, result):
        self._result = result

    def fetchone(self):
        row = self._result.fetchone()
        if row is None:
            return None
        return _Row(row._mapping)

    def fetchall(self):
        return [_Row(row._mapping) for row in self._result.fetchall()]


class _Row:
    """
    Dict-like row object.  Supports both row["key"] and row.key access,
    matching the sqlite3.Row interface the models rely on.
    """

    def __init__(self, mapping):
        self._data = dict(mapping)

    def __getitem__(self, key):
        return self._data[key]

    def __getattr__(self, key):
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(key)

    def keys(self):
        return self._data.keys()

    def __repr__(self):
        return f"<Row {self._data}>"


# ── Public API ────────────────────────────────────────────────────────────────

def get_db() -> _Connection:
    """
    Return a new database connection wrapped in _Connection.

    Usage (identical to the original sqlite3 version):
        with get_db() as conn:
            row = conn.execute("SELECT * FROM students WHERE ...", (...)).fetchone()
    """
    return _Connection(_engine.connect())


def init_db() -> None:
    """
    Create all tables if they do not already exist.
    Safe to call every time the app starts — uses IF NOT EXISTS.

    SERIAL / AUTOINCREMENT:
      PostgreSQL uses SERIAL for auto-increment primary keys.
      SQLite accepts SERIAL too (treats it as INTEGER), so we use
      SERIAL in the schema for both backends.
    """
    schema_sql = """
    CREATE TABLE IF NOT EXISTS students (
        id              SERIAL PRIMARY KEY,
        student_id      TEXT   NOT NULL UNIQUE,
        name            TEXT   NOT NULL,
        line_user_id    TEXT   NOT NULL UNIQUE,
        registered_at   TEXT   NOT NULL
    );

    CREATE TABLE IF NOT EXISTS homework (
        id          SERIAL PRIMARY KEY,
        hw_code     TEXT   NOT NULL UNIQUE,
        title       TEXT   NOT NULL,
        description TEXT   DEFAULT '',
        due_date    TEXT   NOT NULL,
        created_by  TEXT   NOT NULL,
        created_at  TEXT   NOT NULL
    );

    CREATE TABLE IF NOT EXISTS submissions (
        id              SERIAL PRIMARY KEY,
        hw_code         TEXT   NOT NULL,
        student_id      TEXT   NOT NULL,
        submission_link TEXT   NOT NULL,
        submitted_at    TEXT   NOT NULL,
        UNIQUE (hw_code, student_id)
    );

    CREATE TABLE IF NOT EXISTS attendance (
        id           SERIAL PRIMARY KEY,
        student_id   TEXT   NOT NULL,
        date         TEXT   NOT NULL,
        checkin_time TEXT   NOT NULL,
        UNIQUE (student_id, date)
    )
    """
    with get_db() as conn:
        conn.executescript(schema_sql)
    logger.info("Database tables ready ✓ (backend: %s)", _engine.dialect.name)