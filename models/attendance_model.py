"""
models/attendance_model.py
--------------------------
All database operations related to attendance.
"""

from sqlalchemy.exc import IntegrityError
from database import get_db
from utils.time_utils import now_iso, today_str


def checkin_student(student_id: str) -> dict:
    """
    Record a student's check-in for today.

    Returns:
        {"ok": True}  or  {"ok": False, "reason": "..."}
    """
    try:
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO attendance (student_id, date, checkin_time)
                VALUES (?, ?, ?)
                """,
                (student_id, today_str(), now_iso()),
            )
        return {"ok": True}
    except IntegrityError:
        return {"ok": False, "reason": "You have already checked in today."}


def get_attendance_for_date(date: str) -> list:
    """Return all attendance records for a given date (YYYY-MM-DD)."""
    with get_db() as conn:
        return conn.execute(
            """
            SELECT a.*, s.name, s.student_id
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.date = ?
            ORDER BY a.checkin_time
            """,
            (date,),
        ).fetchall()


def get_present_student_ids_for_date(date: str) -> set[str]:
    """Return student_ids who checked in on a given date."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT student_id FROM attendance WHERE date = ?",
            (date,),
        ).fetchall()
    return {row["student_id"] for row in rows}