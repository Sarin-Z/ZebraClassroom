"""
database.py
-----------
SQLite connection pool and schema bootstrap.

Call `init_db()` once at startup to create all tables.
Use `get_db()` to get a connection anywhere in the codebase.
"""

import sqlite3
import logging
from config import Config

logger = logging.getLogger(__name__)


def get_db() -> sqlite3.Connection:
    """
    Return a new SQLite connection with row_factory set so rows behave
    like dictionaries (access columns by name).
    """
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row          # row["column_name"] syntax
    conn.execute("PRAGMA foreign_keys = ON") # enforce FK constraints
    return conn


def init_db() -> None:
    """
    Create all tables if they do not already exist.
    Safe to call every time the app starts.
    """
    schema_sql = """
    -- ── Students ────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS students (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id      TEXT    NOT NULL UNIQUE,   -- e.g. "65012345"
        name            TEXT    NOT NULL,
        line_user_id    TEXT    NOT NULL UNIQUE,   -- LINE UID
        registered_at   TEXT    NOT NULL           -- ISO-8601 datetime
    );

    -- ── Homework assignments ─────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS homework (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        hw_code     TEXT    NOT NULL UNIQUE,   -- e.g. "hw1"
        title       TEXT    NOT NULL,
        description TEXT    DEFAULT '',
        due_date    TEXT    NOT NULL,           -- "YYYY-MM-DD"
        created_by  TEXT    NOT NULL,           -- teacher LINE UID
        created_at  TEXT    NOT NULL
    );

    -- ── Submissions ──────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS submissions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        hw_code         TEXT    NOT NULL,
        student_id      TEXT    NOT NULL,
        submission_link TEXT    NOT NULL,
        submitted_at    TEXT    NOT NULL,
        FOREIGN KEY (hw_code)    REFERENCES homework(hw_code),
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        UNIQUE (hw_code, student_id)           -- one submission per hw
    );

    -- ── Attendance ───────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS attendance (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id   TEXT    NOT NULL,
        date         TEXT    NOT NULL,          -- "YYYY-MM-DD"
        checkin_time TEXT    NOT NULL,          -- ISO-8601 datetime
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        UNIQUE (student_id, date)               -- one check-in per day
    );
    """
    with get_db() as conn:
        conn.executescript(schema_sql)
    logger.info("Database initialised at '%s'", Config.DATABASE_PATH)
