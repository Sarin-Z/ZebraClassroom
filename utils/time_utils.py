"""
utils/time_utils.py
-------------------
Consistent timestamp helpers used across the project.
All times are stored in UTC ISO-8601 format.
"""

from datetime import datetime, timezone


def now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def today_str() -> str:
    """Return today's UTC date as YYYY-MM-DD."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def is_valid_date(date_str: str) -> bool:
    """Return True if date_str is a valid YYYY-MM-DD date."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
