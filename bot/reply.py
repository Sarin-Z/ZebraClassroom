"""
bot/reply.py
------------
Helper functions that build nicely formatted reply strings.

All message text is defined here, keeping command handlers free of
presentation logic (separation of concerns).
"""


# ── Generic ───────────────────────────────────────────────────────────────────

def ok(message: str) -> str:
    return f"✅ {message}"


def error(message: str) -> str:
    return f"❌ {message}"


def warn(message: str) -> str:
    return f"⚠️ {message}"


# ── Registration ──────────────────────────────────────────────────────────────

def registration_success(name: str, student_id: str) -> str:
    return (
        "✅ Registration successful!\n"
        f"Name       : {name}\n"
        f"Student ID : {student_id}"
    )


# ── Homework assignment ───────────────────────────────────────────────────────

def homework_created(hw_code: str, title: str, due_date: str) -> str:
    return (
        f"📚 Homework '{hw_code}' created.\n"
        f"Title : {title}\n"
        f"Due   : {due_date}"
    )


def homework_list(rows) -> str:
    if not rows:
        return "📭 No homework assignments yet."
    lines = ["📋 Homework List\n" + "─" * 30]
    for row in rows:
        lines.append(f"[{row['hw_code']}] {row['title']}\n  Due: {row['due_date']}")
    return "\n\n".join(lines)


# ── Submission ────────────────────────────────────────────────────────────────

def submission_success(hw_code: str) -> str:
    return f"✅ Submission recorded for '{hw_code}'."


# ── Status ────────────────────────────────────────────────────────────────────

def homework_status(all_hw, submitted_codes: set[str]) -> str:
    if not all_hw:
        return "📭 No homework has been assigned yet."
    lines = ["📊 Homework Status\n" + "─" * 30]
    for hw in all_hw:
        icon = "✔" if hw["hw_code"] in submitted_codes else "❌"
        lines.append(f"{hw['hw_code']}  {icon}  (due {hw['due_date']})")
    return "\n".join(lines)


# ── Missing submissions ───────────────────────────────────────────────────────

def missing_students(hw_code: str, missing_names: list[str]) -> str:
    if not missing_names:
        return f"🎉 All students submitted '{hw_code}'!"
    names_block = "\n".join(f"  • {n}" for n in sorted(missing_names))
    return f"📌 Students missing '{hw_code}'\n" + "─" * 30 + f"\n{names_block}"


# ── Attendance ────────────────────────────────────────────────────────────────

def checkin_success(name: str) -> str:
    return f"✅ Check-in recorded. Good morning, {name}!"


def attendance_report(date: str, present: list, absent: list) -> str:
    total = len(present) + len(absent)
    lines = [
        f"📅 Attendance Report — {date}",
        "─" * 30,
        f"Present : {len(present)}/{total}",
        f"Absent  : {len(absent)}/{total}",
    ]
    if present:
        lines.append("\n✅ Present:")
        lines += [f"  • {n}" for n in present]
    if absent:
        lines.append("\n❌ Absent:")
        lines += [f"  • {n}" for n in absent]
    return "\n".join(lines)


# ── Help ──────────────────────────────────────────────────────────────────────

HELP_STUDENT = """\
📖 Student Commands
─────────────────────────────
register <student_id> <name>
  → Register your account

submit <hw_code> <link>
  → Submit a homework link

status
  → See your submission status

checkin
  → Record today's attendance

help
  → Show this message"""

HELP_TEACHER = """\
📖 Teacher Commands
─────────────────────────────
assign <hw_code> <due_date> <title>
  → Create a new homework (date: YYYY-MM-DD)

list_hw
  → List all homework assignments

missing <hw_code>
  → List students who haven't submitted

attendance_report
  → Today's attendance summary

(All student commands also available)"""
