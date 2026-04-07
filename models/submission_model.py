"""
models/submission_model.py
--------------------------
All database operations related to homework submissions.
"""

import sqlite3
from database import get_db
from utils.time_utils import now_iso


def create_submission(hw_code: str, student_id: str, submission_link: str) -> dict:
    """
    Record a student's submission for a homework assignment.

    Returns:
        {"ok": True}  or  {"ok": False, "reason": "..."}
    """
    try:
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO submissions (hw_code, student_id, submission_link, submitted_at)
                VALUES (?, ?, ?, ?)
                """,
                (hw_code, student_id, submission_link, now_iso()),
            )
        return {"ok": True}
    except sqlite3.IntegrityError:
        return {
            "ok": False,
            "reason": f"You have already submitted '{hw_code}'. Each student may submit once.",
        }


def get_submission(hw_code: str, student_id: str) -> sqlite3.Row | None:
    """Return the submission row for a (hw_code, student_id) pair, or None."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM submissions WHERE hw_code = ? AND student_id = ?",
            (hw_code, student_id),
        ).fetchone()


def get_submitted_student_ids(hw_code: str) -> set[str]:
    """Return the set of student_ids who submitted a specific homework."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT student_id FROM submissions WHERE hw_code = ?",
            (hw_code,),
        ).fetchall()
    return {row["student_id"] for row in rows}


def get_submissions_by_student(student_id: str) -> list[sqlite3.Row]:
    """Return all submissions made by a specific student."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM submissions WHERE student_id = ? ORDER BY submitted_at",
            (student_id,),
        ).fetchall()
