"""
commands/status.py
------------------
Handles: status

Shows a student their submission status across all homework assignments.
"""

from bot.reply import homework_status, error
from models.student_model import get_student_by_line_id
from models.homework_model import get_all_homework
from models.submission_model import get_submissions_by_student


def handle(args: list[str], line_user_id: str) -> str:
    student = get_student_by_line_id(line_user_id)
    if not student:
        return error("You are not registered. Use: register <student_id> <name>")

    all_hw = get_all_homework()
    submissions = get_submissions_by_student(student["student_id"])
    submitted_codes = {s["hw_code"] for s in submissions}

    return homework_status(all_hw, submitted_codes)
