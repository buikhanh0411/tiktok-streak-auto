# TikTok Auto Streak Messenger

A SOLID-based browser automation tool for automated TikTok messaging, featuring a Telegram bot for easy management and scheduling.

## Features
- **SOLID Design:** Easy to swap browser engines or social platforms.
- **Multiple Engines:** Supports **Playwright** and **nodriver** (to bypass "browser not secure" detection).
- **Telegram Bot:** Manage streaks, check cookie health, and upload config files directly via Telegram.
- **Automated Scheduling:** The bot automatically sends daily streaks at random times (8 AM - 11 AM) and performs health checks.
- **Cookie Login:** Capture cookies manually and use them for automation.
- **CLI Interface:** Simple commands for login and manual sending.
- **Docker Support:** Run the bot 24/7 in a containerized environment.

## Setup

### Environment Variables
Create a `.env` file in the root directory:
```env
TELEGRAM_TOKEN=your_telegram_bot_token
ALLOWED_USER_ID=your_telegram_user_id
TZ=Asia/Ho_Chi_Minh
```

### Option 1: Docker (Recommended for Bot)
1. Build and start the container:
   ```bash
   docker-compose up -d
   ```
2. The bot will start and you can interact with it via Telegram.

### Option 2: Local Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Login to TikTok (Local only):
   ```bash
   # Using nodriver (better for bypassing detection)
   python src/cli/main.py login --engine nodriver
   ```
   *Follow the instructions in the terminal. Once logged in, press Enter to save cookies.*

3. Run the Bot:
   ```bash
   python src/bot/main.py
   ```

## Configuration Files
The bot and CLI use files in the `data/` directory:
- `data/cookies.json`: Captured session cookies.
- `data/config/users.txt`: List of TikTok nicknames (one per line).
- `data/config/messages.txt`: Random message templates (one per line).

**Tip:** You can update these files by sending them as documents to the Telegram bot.

## CLI Commands
```bash
# Check cookie health
python src/cli/main.py check-cookies --engine playwright

# Send manual streak
python src/cli/main.py send --engine playwright --users "user1,user2" --message "Hello!"
```

## Telegram Bot Commands
- `/start` - Welcome message and help.
- `/status` - Show cookie health and streak stats.
- `/check_cookies` - Manually trigger a health check.
- `/send_streak` - Manually trigger the daily streak.
- `/send_footer` - Force send weekly instructions to all users.
- `/change_user` - Instructions to update recipients.


