"""
models/homework_model.py
------------------------
All database operations related to homework assignments.
"""

from sqlalchemy.exc import IntegrityError
from database import get_db
from utils.time_utils import now_iso


def create_homework(
    hw_code: str,
    title: str,
    due_date: str,
    created_by: str,
    description: str = "",
) -> dict:
    """
    Create a new homework assignment.

    Returns:
        {"ok": True}  or  {"ok": False, "reason": "..."}
    """
    try:
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO homework (hw_code, title, description, due_date, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (hw_code, title, description, due_date, created_by, now_iso()),
            )
        return {"ok": True}
    except IntegrityError:
        return {"ok": False, "reason": f"Homework code '{hw_code}' already exists."}


def get_homework(hw_code: str):
    """Return the homework row for a given hw_code, or None."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM homework WHERE hw_code = ?",
            (hw_code,),
        ).fetchone()


def get_all_homework() -> list:
    """Return all homework assignments ordered by due date."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM homework ORDER BY due_date"
        ).fetchall()