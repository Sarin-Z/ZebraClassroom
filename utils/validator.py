"""
utils/validator.py
------------------
Input validation helpers used by command handlers.
"""

import re


def is_valid_student_id(student_id: str) -> bool:
    """
    Student IDs must be 5-12 alphanumeric characters.
    Adjust the regex to match your institution's format.
    """
    return bool(re.fullmatch(r"[A-Za-z0-9]{5,12}", student_id))


def is_valid_hw_code(hw_code: str) -> bool:
    """
    Homework codes must be 2-20 alphanumeric characters (letters, digits, hyphens).
    Examples: hw1, hw-2, midterm, final-project
    """
    return bool(re.fullmatch(r"[A-Za-z0-9\-]{2,20}", hw_code))


def is_valid_url(url: str) -> bool:
    """Basic check that the submission link looks like a URL."""
    return url.startswith("http://") or url.startswith("https://")


def is_valid_name(name: str) -> bool:
    """Names must be 1-50 characters."""
    return 1 <= len(name.strip()) <= 50
