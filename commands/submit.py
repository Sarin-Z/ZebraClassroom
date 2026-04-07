"""
commands/submit.py
------------------
Handles: submit <hw_code> <link>

Students submit a URL as proof of their work.
"""

from bot.reply import submission_success, error
from models.student_model import get_student_by_line_id
from models.homework_model import get_homework
from models.submission_model import create_submission
from utils.validator import is_valid_hw_code, is_valid_url


def handle(args: list[str], line_user_id: str) -> str:
    if len(args) < 2:
        return error(
            "Usage: submit <hw_code> <link>\n"
            "Example: submit hw1 https://github.com/alice/hw1"
        )

    hw_code = args[0].lower()
    link = args[1]

    # ── Validate inputs ───────────────────────────────────────────────────
    if not is_valid_hw_code(hw_code):
        return error("Invalid homework code.")

    if not is_valid_url(link):
        return error("Submission link must start with http:// or https://")

    # ── Check student is registered ───────────────────────────────────────
    student = get_student_by_line_id(line_user_id)
    if not student:
        return error("You are not registered. Use: register <student_id> <name>")

    # ── Check homework exists ─────────────────────────────────────────────
    hw = get_homework(hw_code)
    if not hw:
        return error(f"Homework '{hw_code}' does not exist.")

    # ── Record submission ─────────────────────────────────────────────────
    result = create_submission(hw_code, student["student_id"], link)

    if result["ok"]:
        return submission_success(hw_code)
    else:
        return error(result["reason"])
