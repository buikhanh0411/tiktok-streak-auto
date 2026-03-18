# TikTok Auto Streak Messenger

A SOLID-based browser automation tool for automated TikTok messaging.

## Features
- **SOLID Design:** Easy to swap browser engines or social platforms.
- **Multiple Engines:** Supports **Playwright** and **nodriver** (to bypass "browser not secure" detection).
- **Cookie Login:** Capture cookies manually and use them for automation.
- **CLI Interface:** Simple commands for login and sending messages.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Login to TikTok:
   ```bash
   # Using nodriver (default, better for bypassing detection)
   python src/cli/main.py login --engine nodriver
   
   # Or using playwright
   python src/cli/main.py login --engine playwright
   ```
   *Follow the instructions in the terminal. Once logged in, press Enter to save cookies.*

3. Send messages:
   ```bash
   python src/cli/main.py send --engine nodriver --users "khanhbi347,another_user" --message "Hi from automation!"
   ```

## Architecture
- **Interfaces:** `IBrowserEngine` and `ISocialPlatform` define the contracts.
- **Engines:** `PlaywrightEngine` implements browser automation.
- **Platforms:** `TikTokPlatform` implements TikTok-specific logic.
- **Messenger:** Orchestrates engines and platforms.
