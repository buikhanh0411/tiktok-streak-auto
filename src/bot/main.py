import os
import sys
import logging
import asyncio
import random
import html
from datetime import datetime
from functools import wraps

# Add the project root to sys.path for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from telegram import Update, Document, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue

from src.engines.playwright_engine import PlaywrightEngine
from src.platforms.tiktok import TikTokPlatform
from src.core.messenger import Messenger
from src.core import config, messages

# Environment Variables
TELEGRAM_TOKEN = config.TELEGRAM_TOKEN
ALLOWED_USER_ID = config.ALLOWED_USER_ID

# File Paths
COOKIES_FILE = config.COOKIES_FILE
USERS_FILE = config.USERS_FILE
MESSAGES_FILE = config.MESSAGES_FILE

# Logging Setup
logging.basicConfig(
    format=config.LOG_FORMAT,
    level=config.LOG_LEVEL
)
logger = logging.getLogger(__name__)

def restricted(func):
    """Decorator to restrict access to a specific Telegram user ID."""
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != ALLOWED_USER_ID:
            logger.warning(f"Unauthorized access attempt by ID: {user_id}")
            await update.message.reply_text(messages.UNAUTHORIZED_ACCESS)
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

async def get_messenger_and_engine(headless=config.HEADLESS):
    """Helper to initialize the engine and messenger."""
    engine = PlaywrightEngine()
    platform = TikTokPlatform(engine)
    messenger = Messenger(engine, platform, cookie_file=COOKIES_FILE)
    return messenger, engine

@restricted
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message and command list."""
    await update.message.reply_text(messages.WELCOME_TEXT, parse_mode='HTML')

@restricted
async def change_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt the user to upload a new users.txt file."""
    await update.message.reply_text(messages.CHANGE_USER_TEXT, parse_mode='HTML')

@restricted
async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current bot status."""
    messenger, _ = await get_messenger_and_engine()
    state = messenger._state
    last_sent = state.get("last_footer_sent", "Never")
    
    status_text = messages.STATUS_TEXT_TEMPLATE.format(
        last_sent=html.escape(str(last_sent)),
        cookies_status='✅ Exists' if os.path.exists(COOKIES_FILE) else '❌ Missing',
        users_count=sum(1 for _ in open(USERS_FILE)) if os.path.exists(USERS_FILE) else '❌ Missing',
        messages_count=sum(1 for _ in open(MESSAGES_FILE)) if os.path.exists(MESSAGES_FILE) else '❌ Missing'
    )
    await update.message.reply_text(status_text, parse_mode='HTML')

@restricted
async def check_cookies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual cookie health check."""
    await update.message.reply_text(messages.CHECKING_COOKIES, parse_mode='HTML')
    messenger, _ = await get_messenger_and_engine(headless=config.HEADLESS)
    
    try:
        success = await messenger.check_cookies_health(headless=config.HEADLESS)
        if success:
            await update.message.reply_text(messages.COOKIES_HEALTHY, parse_mode='HTML')
        else:
            await update.message.reply_text(messages.COOKIES_EXPIRED, parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(messages.ERROR_HEALTH_CHECK.format(error=html.escape(str(e))), parse_mode='HTML')

@restricted
async def send_streak_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual streak trigger."""
    if not os.path.exists(USERS_FILE) or not os.path.exists(MESSAGES_FILE):
        await update.message.reply_text(messages.MISSING_FILES, parse_mode='HTML')
        return
        
    await update.message.reply_text(messages.STARTING_STREAK, parse_mode='HTML')
    
    messenger, engine = await get_messenger_and_engine(headless=config.HEADLESS)
    
    with open(USERS_FILE, "r") as f:
        nicknames = [line.strip() for line in f if line.strip()]
    
    with open(MESSAGES_FILE, "r") as f:
        templates = [line.strip() for line in f if line.strip()]

    try:
        await messenger.run_streak(nicknames, templates, headless=config.HEADLESS)
        await update.message.reply_text(messages.STREAK_COMPLETED, parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(messages.STREAK_FAILED.format(error=html.escape(str(e))), parse_mode='HTML')

@restricted
async def send_footer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual trigger for the weekly footer message."""
    if not os.path.exists(USERS_FILE) or not os.path.exists(MESSAGES_FILE):
        await update.message.reply_text(messages.MISSING_FILES, parse_mode='HTML')
        return
        
    await update.message.reply_text(messages.STARTING_FORCED_FOOTER, parse_mode='HTML')
    
    messenger, engine = await get_messenger_and_engine(headless=config.HEADLESS)
    
    try:
        with open(USERS_FILE, "r") as f:
            nicknames = [line.strip() for line in f if line.strip()]
        with open(MESSAGES_FILE, "r") as f:
            templates = [line.strip() for line in f if line.strip()]

        # force=True bypasses the "already run today" check
        # footer_only=True ensures only the footer is sent
        await messenger.run_streak(nicknames, templates, footer_only=True, force=True, headless=config.HEADLESS)
        await update.message.reply_text(messages.FOOTER_COMPLETED, parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(messages.RUN_FAILED.format(error=html.escape(str(e))), parse_mode='HTML')

@restricted
async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads for cookies, users, and messages."""
    if not update.message.document:
        return
        
    doc: Document = update.message.document
    file_name = doc.file_name.lower()
    
    target_path = None
    if file_name == "cookies.json":
        target_path = COOKIES_FILE
    elif file_name == "users.txt":
        target_path = USERS_FILE
    elif file_name == "messages.txt":
        target_path = MESSAGES_FILE
    
    if target_path:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        new_file = await context.bot.get_file(doc.file_id)
        await new_file.download_to_drive(target_path)
        
        extra_info = ""
        if file_name == "users.txt":
            count = sum(1 for _ in open(target_path))
            extra_info = f" (Loaded {count} users)"
            
        await update.message.reply_text(messages.FILE_RECEIVED.format(file_name=html.escape(file_name), extra_info=html.escape(extra_info)), parse_mode='HTML')
    else:
        await update.message.reply_text(messages.FILE_NOT_RECOGNIZED, parse_mode='HTML')

async def daily_health_check_job(context: ContextTypes.DEFAULT_TYPE):
    """Automatic job for checking cookies and notifying user."""
    messenger, _ = await get_messenger_and_engine(headless=config.HEADLESS)
    success = await messenger.check_cookies_health(headless=config.HEADLESS)
    
    if success:
        await context.bot.send_message(chat_id=ALLOWED_USER_ID, text=messages.DAILY_HEALTH_HEALTHY, parse_mode='HTML')
    else:
        await context.bot.send_message(chat_id=ALLOWED_USER_ID, text=messages.DAILY_HEALTH_EXPIRED, parse_mode='HTML')

async def post_init(application):
    """Set bot commands in the Telegram menu."""
    commands = [
        BotCommand("start", "Show welcome message"),
        BotCommand("check_cookies", "Check login status"),
        BotCommand("send_streak", "Start daily streak"),
        BotCommand("send_footer", "Force send weekly footer"),
        BotCommand("change_user", "Update recipients"),
        BotCommand("status", "Show bot status"),
        BotCommand("help", "Show help")
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands have been set.")

async def daily_streak_job(context: ContextTypes.DEFAULT_TYPE):
    """Automatic job for sending the daily streak."""
    if not os.path.exists(USERS_FILE) or not os.path.exists(MESSAGES_FILE):
        await context.bot.send_message(chat_id=ALLOWED_USER_ID, text=messages.AUTO_STREAK_MISSING_FILES, parse_mode='HTML')
        return

    await context.bot.send_message(chat_id=ALLOWED_USER_ID, text=messages.AUTO_STREAK_STARTING, parse_mode='HTML')
    
    messenger, engine = await get_messenger_and_engine(headless=config.HEADLESS)
    
    try:
        with open(USERS_FILE, "r") as f:
            nicknames = [line.strip() for line in f if line.strip()]
        with open(MESSAGES_FILE, "r") as f:
            templates = [line.strip() for line in f if line.strip()]

        await messenger.run_streak(nicknames, templates, headless=config.HEADLESS)
        await context.bot.send_message(chat_id=ALLOWED_USER_ID, text=messages.AUTO_STREAK_COMPLETED, parse_mode='HTML')
    except Exception as e:
        await context.bot.send_message(chat_id=ALLOWED_USER_ID, text=messages.AUTO_STREAK_ERROR.format(error=html.escape(str(e))), parse_mode='HTML')

def schedule_daily_streak(job_queue: JobQueue):
    """Schedule the streak job daily at a random time between 8 AM and 11 AM."""
    hour = random.randint(8, 11)
    minute = random.randint(0, 59)
    job_queue.run_daily(daily_streak_job, time=datetime.strptime(f"{hour}:{minute}", "%H:%M").time())
    logger.info(f"Daily streak scheduled at {hour:02d}:{minute:02d}")

def schedule_random_health_check(job_queue: JobQueue):
    """Schedule the health check daily at a random time between 8 AM and 10 PM."""
    hour = random.randint(8, 22)
    minute = random.randint(0, 59)
    job_queue.run_daily(daily_health_check_job, time=datetime.strptime(f"{hour}:{minute}", "%H:%M").time())
    logger.info(f"Health check scheduled daily at {hour:02d}:{minute:02d}")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN or ALLOWED_USER_ID == 0:
        print("❌ CRITICAL ERROR: TELEGRAM_TOKEN or ALLOWED_USER_ID missing from environment!")
        exit(1)

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(post_init).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", start_handler))
    application.add_handler(CommandHandler("status", status_handler))
    application.add_handler(CommandHandler("check_cookies", check_cookies_handler))
    application.add_handler(CommandHandler("send_streak", send_streak_handler))
    application.add_handler(CommandHandler("send_footer", send_footer_handler))
    application.add_handler(CommandHandler("change_user", change_user_handler))
    application.add_handler(MessageHandler(filters.Document.ALL, document_handler))

    # Scheduler
    schedule_daily_streak(application.job_queue)
    schedule_random_health_check(application.job_queue)

    print("🚀 Bot is starting...")
    application.run_polling()
