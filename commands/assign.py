"""
commands/assign.py
------------------
Handles: assign <hw_code> <due_date> <title>
Teacher-only command.

Example: assign hw1 2026-04-30 LinkedListImplementation
"""

from bot.reply import homework_created, error
from models.homework_model import create_homework
from utils.validator import is_valid_hw_code
from utils.time_utils import is_valid_date


def handle(args: list[str], line_user_id: str) -> str:
    """
    Expected args: [hw_code, due_date, title...]
    Title may be multi-word; everything after due_date is joined.
    """
    if len(args) < 3:
        return error(
            "Usage: assign <hw_code> <due_date> <title>\n"
            "Example: assign hw1 2026-04-30 LinkedListImplementation"
        )

    hw_code = args[0].lower()
    due_date = args[1]
    title = " ".join(args[2:])

    if not is_valid_hw_code(hw_code):
        return error("Invalid homework code. Use 2-20 letters, digits, or hyphens.")

    if not is_valid_date(due_date):
        return error("Invalid date format. Use YYYY-MM-DD.")

    result = create_homework(
        hw_code=hw_code,
        title=title,
        due_date=due_date,
        created_by=line_user_id,
    )

    if result["ok"]:
        return homework_created(hw_code, title, due_date)
    else:
        return error(result["reason"])
