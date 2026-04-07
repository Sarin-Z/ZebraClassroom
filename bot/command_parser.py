"""
bot/command_parser.py
---------------------
Parse a raw LINE message text into a (command, args) tuple.

The parser is intentionally simple:
  - first token  → command name (lowercased)
  - remaining    → list of string arguments

Example:
    "submit hw1 https://github.com/alice/hw1"
    → ("submit", ["hw1", "https://github.com/alice/hw1"])
"""

from dataclasses import dataclass


@dataclass
class ParsedCommand:
    name: str           # e.g. "submit"
    args: list[str]     # e.g. ["hw1", "https://..."]
    raw: str            # original message text


def parse(text: str) -> ParsedCommand | None:
    """
    Parse a message string into a ParsedCommand.

    Returns None if the message is empty or doesn't look like a command.
    All commands are case-insensitive.
    """
    text = text.strip()
    if not text:
        return None

    tokens = text.split()
    command = tokens[0].lower()
    args = tokens[1:]

    # Ignore messages that are clearly not bot commands
    # (e.g. ordinary chat messages without a known keyword trigger)
    known_commands = {
        "register", "submit", "status", "checkin", "help",
        "assign", "missing", "list_hw", "attendance_report",
    }
    if command not in known_commands:
        return None

    return ParsedCommand(name=command, args=args, raw=text)
