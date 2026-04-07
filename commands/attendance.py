"""
commands/attendance.py
----------------------
Handles:
  checkin              (student) — record today's attendance
  attendance_report    (teacher) — show today's full report
"""

from bot.reply import checkin_success, attendance_report, error
from models.student_model import get_student_by_line_id, get_all_students
from models.attendance_model import checkin_student, get_present_student_ids_for_date
from utils.time_utils import today_str


def handle_checkin(line_user_id: str) -> str:
    """Student checks in for today."""
    student = get_student_by_line_id(line_user_id)
    if not student:
        return error("You are not registered. Use: register <student_id> <name>")

    result = checkin_student(student["student_id"])
    if result["ok"]:
        return checkin_success(student["name"])
    return error(result["reason"])


def handle_report() -> str:
    """Teacher views today's attendance summary."""
    date = today_str()
    all_students = get_all_students()
    present_ids = get_present_student_ids_for_date(date)

    present_names = [s["name"] for s in all_students if s["student_id"] in present_ids]
    absent_names  = [s["name"] for s in all_students if s["student_id"] not in present_ids]

    return attendance_report(date, present_names, absent_names)
