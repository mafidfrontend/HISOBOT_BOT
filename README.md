## Telegram hisobot bot (aiogram 3 + SQLite)

### What it does
This bot helps a user create a daily end-of-day report in Telegram using `/report`, then review it with inline buttons:
- Send to group
- Edit
- Regenerate
- Cancel

Reports and user names are stored in SQLite. The bot automatically sets the report date to the current local date in `DD.MM` format.

### Setup
1. Create a virtual environment (Python 3.10+ recommended):
   - PowerShell:
     - `python -m venv .venv`
     - `.venv\\Scripts\\Activate.ps1`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Create your `.env` file (copy from example):
   - Rename `.env.example` to `.env`
   - Set:
     - `BOT_TOKEN=...`
     - `GROUP_ID=...`
4. Run the bot:
   - `python bot.py`

### Usage
- `/start` - greeting
- `/report` - create today's report (wizard)
- `/today` - show today's last report
- `/edit` - edit today's last report (only if it was not sent yet)
- `/send` - send today's last report to the group
- `/cancel` - cancel current draft (or delete the unsent draft)

