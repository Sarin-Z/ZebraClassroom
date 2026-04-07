"""
config.py
---------
Central configuration loader. All settings come from environment variables
defined in .env (or set in the hosting platform's dashboard).
"""

import os
from dotenv import load_dotenv

# Load .env file when running locally
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # ── LINE API credentials ──────────────────────────────────────────────
    LINE_CHANNEL_ACCESS_TOKEN: str = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    LINE_CHANNEL_SECRET: str = os.getenv("LINE_CHANNEL_SECRET", "")

    # ── Authorization ─────────────────────────────────────────────────────
    # Comma-separated list of LINE user IDs who have teacher privileges
    _teacher_ids_raw: str = os.getenv("TEACHER_USER_IDS", "")
    TEACHER_USER_IDS: set[str] = {
        uid.strip()
        for uid in _teacher_ids_raw.split(",")
        if uid.strip()
    }

    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "classroom.db")

    # ── Flask ─────────────────────────────────────────────────────────────
    DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    PORT: int = int(os.getenv("PORT", 5000))

    @classmethod
    def validate(cls) -> None:
        """Raise an error early if required credentials are missing."""
        missing = []
        if not cls.LINE_CHANNEL_ACCESS_TOKEN:
            missing.append("LINE_CHANNEL_ACCESS_TOKEN")
        if not cls.LINE_CHANNEL_SECRET:
            missing.append("LINE_CHANNEL_SECRET")
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Copy .env.example to .env and fill in your credentials."
            )
