# 📚 LINE Classroom Management Bot

A production-ready LINE Messaging API bot for managing classroom activities — homework assignments, submissions, and attendance — directly inside a LINE group chat.

---

## ✨ Features

| Feature | Who |
|---|---|
| `register` — Link LINE account to student ID | Student |
| `submit` — Submit a homework link | Student |
| `status` — View personal submission status | Student |
| `checkin` — Record daily attendance | Student |
| `assign` — Create a homework assignment | Teacher |
| `list_hw` — List all homework | Teacher |
| `missing` — See who hasn't submitted | Teacher |
| `attendance_report` — Today's attendance summary | Teacher |
| `help` — Show available commands | Anyone |

---

## 🗂 Project Structure

```
line-classroom-bot/
│
├── app.py                  # Flask app factory + entry point
├── config.py               # All settings from environment variables
├── database.py             # SQLite init + get_db() helper
├── requirements.txt
├── Procfile                # For Render / Railway
├── render.yaml             # One-click Render deploy config
├── .env.example            # Template for your credentials
│
├── bot/
│   ├── webhook.py          # /webhook route + LINE event dispatcher
│   ├── command_parser.py   # Raw text → ParsedCommand
│   └── reply.py            # All reply message strings (presentation layer)
│
├── commands/               # One file per command (thin controllers)
│   ├── register.py
│   ├── assign.py
│   ├── submit.py
│   ├── status.py
│   ├── missing.py
│   ├── list_hw.py
│   ├── attendance.py
│   └── help_cmd.py
│
├── models/                 # All SQL queries (data layer)
│   ├── student_model.py
│   ├── homework_model.py
│   ├── submission_model.py
│   └── attendance_model.py
│
└── utils/                  # Pure helper functions
    ├── auth.py             # is_teacher() check
    ├── validator.py        # Input validation
    └── time_utils.py       # Timestamps
```

---

## 🗄 Database Schema

```sql
CREATE TABLE students (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id    TEXT NOT NULL UNIQUE,   -- e.g. "65012345"
    name          TEXT NOT NULL,
    line_user_id  TEXT NOT NULL UNIQUE,   -- LINE UID
    registered_at TEXT NOT NULL           -- ISO-8601 UTC
);

CREATE TABLE homework (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    hw_code     TEXT NOT NULL UNIQUE,     -- e.g. "hw1"
    title       TEXT NOT NULL,
    description TEXT DEFAULT '',
    due_date    TEXT NOT NULL,            -- "YYYY-MM-DD"
    created_by  TEXT NOT NULL,            -- teacher LINE UID
    created_at  TEXT NOT NULL
);

CREATE TABLE submissions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    hw_code         TEXT NOT NULL,
    student_id      TEXT NOT NULL,
    submission_link TEXT NOT NULL,
    submitted_at    TEXT NOT NULL,
    UNIQUE (hw_code, student_id)          -- one submission per hw
);

CREATE TABLE attendance (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id   TEXT NOT NULL,
    date         TEXT NOT NULL,           -- "YYYY-MM-DD"
    checkin_time TEXT NOT NULL,
    UNIQUE (student_id, date)             -- one check-in per day
);
```

---

## 🚀 Local Setup

### 1. Clone & install

```bash
git clone https://github.com/you/line-classroom-bot.git
cd line-classroom-bot
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Edit `.env`:

```env
LINE_CHANNEL_ACCESS_TOKEN=your_token_here
LINE_CHANNEL_SECRET=your_secret_here
TEACHER_USER_IDS=Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> **How to find your LINE User ID:**
> 1. Start the bot and send any message
> 2. The user ID appears in the server logs: `User Uxxxx issued command: ...`

### 3. Run

```bash
python app.py
# Server starts at http://localhost:5000
```

---

## 🔗 Expose with Ngrok (local testing)

LINE requires a **public HTTPS URL** for webhooks. Ngrok creates one instantly.

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 5000
```

You'll see output like:
```
Forwarding  https://abcd-1234.ngrok-free.app -> http://localhost:5000
```

Copy that HTTPS URL. Then:

1. Go to [LINE Developers Console](https://developers.line.biz/console/)
2. Select your channel → **Messaging API** tab
3. Set **Webhook URL**: `https://abcd-1234.ngrok-free.app/webhook`
4. Click **Verify** — you should see "Success"
5. Enable **Use webhook**

---

## 🧪 Testing Commands

Once the bot is in your LINE group:

```
# Register as a student
register 65012345 Alice

# Teacher creates homework
assign hw1 2026-04-30 LinkedList Implementation

# Student submits
submit hw1 https://github.com/alice/hw1

# Check your status
status

# Check in for attendance
checkin

# Teacher: who hasn't submitted?
missing hw1

# Teacher: today's attendance
attendance_report

# List all homework
list_hw

# Get help
help
```

### Test with curl (webhook simulation)

```bash
# Health check
curl http://localhost:5000/

# Webhook endpoint (LINE signature required for real events)
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"events": []}'
```

---

## ☁️ Deploy to Render (free tier)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Render auto-detects `render.yaml`
5. Set environment variables in the **Environment** tab:
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `TEACHER_USER_IDS`
6. Deploy — your URL will be `https://line-classroom-bot.onrender.com`
7. Update the LINE webhook URL to `https://line-classroom-bot.onrender.com/webhook`

> **Note:** Render free tier spins down after 15 minutes of inactivity. For always-on, upgrade to the $7/month plan or use Railway.

---

## ☁️ Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

railway login
railway init
railway up
```

Set env vars in the Railway dashboard. Railway keeps your service always alive on the free tier.

---

## 🏗 Architecture

```
User sends message in LINE group
        │
        ▼
LINE Platform sends POST to /webhook
        │
        ▼
bot/webhook.py  ──validates signature──▶  abort(400) if invalid
        │
        ▼
bot/command_parser.py  parses text into (command, args)
        │
        ▼
_dispatch()  ──teacher gate──▶  "⛔ Teachers only" if needed
        │
        ▼
commands/*.py  validates input, calls model functions
        │
        ▼
models/*.py  runs SQL via get_db()
        │
        ▼
bot/reply.py  formats the response string
        │
        ▼
LINE Messaging API  sends reply to group
```

---

## 🔒 Security Notes

- **Signature validation** — every webhook request is verified using `X-Line-Signature`
- **Teacher authorization** — teacher commands check `TEACHER_USER_IDS` from env
- **Input validation** — all user input is validated before touching the database
- **Parameterized queries** — all SQL uses `?` placeholders (no SQL injection)
- **No secrets in code** — all credentials live in environment variables

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `flask` | Web server + routing |
| `line-bot-sdk` | LINE Messaging API client |
| `python-dotenv` | Load `.env` files locally |
| `gunicorn` | Production WSGI server |
