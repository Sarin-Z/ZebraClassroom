"""
commands/list_hw.py
-------------------
Handles: list_hw
Teacher-only command.

Lists all homework assignments ordered by due date.
"""

from bot.reply import homework_list
from models.homework_model import get_all_homework


def handle() -> str:
    return homework_list(get_all_homework())
