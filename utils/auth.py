"""
utils/auth.py
-------------
Authorization helpers.

Teacher-only commands are gated behind is_teacher().
Teacher LINE user IDs are configured via the TEACHER_USER_IDS env var.
"""

from config import Config


def is_teacher(line_user_id: str) -> bool:
    """Return True if the LINE user is listed as a teacher."""
    return line_user_id in Config.TEACHER_USER_IDS
