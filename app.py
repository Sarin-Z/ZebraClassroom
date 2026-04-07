"""
app.py
------
Application entry point.

Running:
    python app.py             ← local development
    gunicorn app:app          ← production (Render / Railway)
"""

import logging
from flask import Flask
from config import Config
from database import init_db
from bot.webhook import webhook_bp

# ── Configure logging ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """
    Application factory.
    Validates config, initialises the database, and registers blueprints.
    """
    # Fail fast if LINE credentials are not set
    Config.validate()
    logger.info("Config validated ✓")

    # Create all SQLite tables (safe to call repeatedly)
    init_db()
    logger.info("Database ready ✓")

    app = Flask(__name__)

    # Register the webhook blueprint (adds /webhook route)
    app.register_blueprint(webhook_bp)

    # Simple health-check endpoint — useful for Render / Railway uptime pings
    @app.get("/")
    def health():
        return {"status": "ok", "service": "LINE Classroom Bot"}, 200

    logger.info("Flask app created ✓")
    return app


# Create the app at module level so gunicorn can find `app:app`
app = create_app()


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=Config.PORT)
