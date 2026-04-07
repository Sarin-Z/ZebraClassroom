"""
commands/help_cmd.py
--------------------
Handles: help

Teachers see both the student and teacher command sections.
Students only see the student section.
"""

from bot.reply import HELP_STUDENT, HELP_TEACHER
from utils.auth import is_teacher


def handle(line_user_id: str) -> str:
    if is_teacher(line_user_id):
        return HELP_STUDENT + "\n\n" + HELP_TEACHER
    return HELP_STUDENT
