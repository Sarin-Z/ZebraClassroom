"""
commands/register.py
--------------------
Handles: register <student_id> <name>

Students call this once to link their LINE account to their student ID.
"""

from bot.reply import registration_success, error
from models.student_model import register_student
from utils.validator import is_valid_student_id, is_valid_name


def handle(args: list[str], line_user_id: str) -> str:
    """
    Expected args: [student_id, name]
    Name may contain spaces if provided as remaining tokens.
    """
    if len(args) < 2:
        return error("Usage: register <student_id> <your name>\nExample: register 65012345 Alice")

    student_id = args[0]
    name = " ".join(args[1:])  # allow multi-word names

    if not is_valid_student_id(student_id):
        return error("Invalid student ID. Use 5-12 alphanumeric characters.")

    if not is_valid_name(name):
        return error("Invalid name. Please use 1-50 characters.")

    result = register_student(student_id, name, line_user_id)

    if result["ok"]:
        return registration_success(name, student_id)
    else:
        return error(result["reason"])
