"""
models/student_model.py
-----------------------
All database operations related to students.
"""

import sqlite3
from database import get_db
from utils.time_utils import now_iso


def register_student(student_id: str, name: str, line_user_id: str) -> dict:
    """
    Insert a new student record.

    Returns:
        {"ok": True}  on success
        {"ok": False, "reason": "..."}  on failure
    """
    try:
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO students (student_id, name, line_user_id, registered_at)
                VALUES (?, ?, ?, ?)
                """,
                (student_id, name, line_user_id, now_iso()),
            )
        return {"ok": True}
    except sqlite3.IntegrityError as e:
        if "student_id" in str(e):
            return {"ok": False, "reason": f"Student ID '{student_id}' is already registered."}
        if "line_user_id" in str(e):
            return {"ok": False, "reason": "Your LINE account is already registered."}
        return {"ok": False, "reason": "Registration failed due to a database conflict."}


def get_student_by_line_id(line_user_id: str) -> sqlite3.Row | None:
    """Return the student row for a given LINE user ID, or None."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM students WHERE line_user_id = ?",
            (line_user_id,),
        ).fetchone()


def get_student_by_student_id(student_id: str) -> sqlite3.Row | None:
    """Return the student row for a given student ID, or None."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,),
        ).fetchone()


def get_all_students() -> list[sqlite3.Row]:
    """Return all registered students."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM students ORDER BY student_id"
        ).fetchall()
