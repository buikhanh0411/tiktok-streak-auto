import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env if it exists
load_dotenv()

# Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))
TIMEZONE = os.getenv("TZ", "Asia/Ho_Chi_Minh")

# File Paths
DATA_DIR = "data"
CONFIG_DIR = os.path.join(DATA_DIR, "config")

COOKIES_FILE = os.path.join(DATA_DIR, "cookies.json")
STATE_FILE = os.path.join(DATA_DIR, "state.json")
USERS_FILE = os.path.join(CONFIG_DIR, "users.txt")
MESSAGES_FILE = os.path.join(CONFIG_DIR, "messages.txt")

# Ensure directories exist
os.makedirs(CONFIG_DIR, exist_ok=True)

# Global start date for the streak counter
STREAK_START_DATE = datetime(2026, 3, 17)

# TikTok Constants
TIKTOK_BASE_URL = "https://www.tiktok.com"
TIKTOK_MESSAGES_URL = f"{TIKTOK_BASE_URL}/messages"

# Logging Setup
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
