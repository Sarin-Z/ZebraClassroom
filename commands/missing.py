"""
commands/missing.py
-------------------
Handles: missing <hw_code>
Teacher-only command.

Lists every registered student who has NOT submitted the given homework.
"""

from bot.reply import missing_students, error
from models.homework_model import get_homework
from models.student_model import get_all_students
from models.submission_model import get_submitted_student_ids
from utils.validator import is_valid_hw_code


def handle(args: list[str], line_user_id: str) -> str:
    if not args:
        return error("Usage: missing <hw_code>\nExample: missing hw1")

    hw_code = args[0].lower()

    if not is_valid_hw_code(hw_code):
        return error("Invalid homework code.")

    hw = get_homework(hw_code)
    if not hw:
        return error(f"Homework '{hw_code}' does not exist.")

    all_students = get_all_students()
    submitted_ids = get_submitted_student_ids(hw_code)

    missing_names = [
        s["name"]
        for s in all_students
        if s["student_id"] not in submitted_ids
    ]

    return missing_students(hw_code, missing_names)
