"""
bot/webhook.py
--------------
Flask Blueprint that registers the /webhook route and routes every
incoming LINE text message to the appropriate command handler.

Flow:
  LINE Platform → POST /webhook
    → validate signature
    → parse text into ParsedCommand
    → dispatch to command handler
    → send reply via LINE Messaging API
"""

import logging
from flask import Blueprint, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from config import Config
from bot.command_parser import parse
from utils.auth import is_teacher

# ── Import all command handlers ───────────────────────────────────────────────
import commands.register   as cmd_register
import commands.assign     as cmd_assign
import commands.submit     as cmd_submit
import commands.status     as cmd_status
import commands.missing    as cmd_missing
import commands.list_hw    as cmd_list_hw
import commands.help_cmd   as cmd_help
from commands.attendance import handle_checkin, handle_report

logger = logging.getLogger(__name__)

# Blueprint lets us keep routing code out of app.py
webhook_bp = Blueprint("webhook", __name__)

# LINE SDK objects — created once at module load time
handler       = WebhookHandler(Config.LINE_CHANNEL_SECRET)
configuration = Configuration(access_token=Config.LINE_CHANNEL_ACCESS_TOKEN)


# ── Route ─────────────────────────────────────────────────────────────────────

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    """
    Entry point for all LINE webhook events.
    LINE sends a POST request here whenever something happens in the chat.
    """
    signature = request.headers.get("X-Line-Signature", "")
    body      = request.get_data(as_text=True)

    logger.debug("Webhook received: %s", body[:200])

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.warning("Invalid LINE signature — possible spoofed request")
        abort(400)

    return "OK", 200


# ── Event handler ─────────────────────────────────────────────────────────────

@handler.add(MessageEvent, message=TextMessageContent)
def on_text_message(event: MessageEvent):
    """
    Called for every text message received in the group (or direct chat).
    Parses the text, dispatches to the right command handler, and replies.
    """
    user_id    = event.source.user_id
    text       = event.message.text

    # Parse the message — returns None for non-command chat
    cmd = parse(text)
    if cmd is None:
        return  # ordinary chat message; ignore silently

    logger.info("User %s issued command: %s", user_id, cmd.name)

    reply_text = _dispatch(cmd.name, cmd.args, user_id)

    if reply_text:
        _send_reply(event.reply_token, reply_text)


# ── Dispatcher ────────────────────────────────────────────────────────────────

# Commands restricted to teachers
_TEACHER_ONLY = {"assign", "missing", "list_hw", "attendance_report"}


def _dispatch(name: str, args: list[str], user_id: str) -> str:
    """
    Route a parsed command to its handler function.
    Returns the reply string to send back to the user.
    """
    # ── Teacher-only gate ─────────────────────────────────────────────────
    if name in _TEACHER_ONLY and not is_teacher(user_id):
        return "⛔ This command is for teachers only."

    # ── Route ─────────────────────────────────────────────────────────────
    match name:
        case "register":
            return cmd_register.handle(args, user_id)
        case "submit":
            return cmd_submit.handle(args, user_id)
        case "status":
            return cmd_status.handle(args, user_id)
        case "checkin":
            return handle_checkin(user_id)
        case "help":
            return cmd_help.handle(user_id)
        case "assign":
            return cmd_assign.handle(args, user_id)
        case "missing":
            return cmd_missing.handle(args, user_id)
        case "list_hw":
            return cmd_list_hw.handle()
        case "attendance_report":
            return handle_report()
        case _:
            return "❓ Unknown command. Type 'help' to see available commands."


# ── Reply sender ──────────────────────────────────────────────────────────────

def _send_reply(reply_token: str, text: str) -> None:
    """Send a single text reply via the LINE Messaging API."""
    try:
        with ApiClient(configuration) as api_client:
            api = MessagingApi(api_client)
            api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=text)],
                )
            )
        logger.debug("Reply sent (token: %s...)", reply_token[:8])
    except Exception as e:
        logger.error("Failed to send reply: %s", e)
