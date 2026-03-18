# Bot Messages (Telegram)
WELCOME_TEXT = (
    "🤖 <b>TikTok Auto Streak Bot</b>\n\n"
    "Welcome! I am ready to manage your TikTok streaks.\n\n"
    "<b>Commands:</b>\n"
    "/check_cookies - Check if your login is still valid\n"
    "/send_streak - Start the daily message streak\n"
    "/change_user - Update the TikTok recipients list\n"
    "/status - Show cookie status and streak stats\n"
    "/help - Show this message\n\n"
    "📂 <b>How to update files:</b>\n"
    "Simply send me <code>cookies.json</code>, <code>users.txt</code>, or <code>messages.txt</code> as a document to update them."
)

CHANGE_USER_TEXT = (
    "📝 <b>Changing User List</b>\n\n"
    "Please send me a new <code>users.txt</code> file now.\n"
    "Make sure each nickname is on a new line."
)

STATUS_TEXT_TEMPLATE = (
    "📈 <b>Bot Status</b>\n\n"
    "📍 <b>Last Weekly Message:</b> <code>{last_sent}</code>\n"
    "🍪 <b>Cookies:</b> {cookies_status}\n"
    "👥 <b>Users:</b> {users_count}\n"
    "💬 <b>Messages:</b> {messages_count}"
)

CHECKING_COOKIES = "🔍 <b>Checking cookie health...</b> Please wait."
COOKIES_HEALTHY = "✅ <b>Cookies are HEALTHY!</b> You're good to go."
COOKIES_EXPIRED = "❌ <b>Cookies EXPIRED!</b> Please re-capture locally and send me a new <code>cookies.json</code>."
ERROR_HEALTH_CHECK = "⚠️ <b>Error during health check:</b> {error}"

MISSING_FILES = "❌ <b>Missing users.txt or messages.txt!</b> Upload them first."
STARTING_STREAK = "🚀 <b>Starting streak run...</b> I will notify you when finished."
STREAK_COMPLETED = "✨ <b>Streak run completed!</b>"
STREAK_FAILED = "❌ <b>Streak run failed:</b> {error}"

STARTING_FORCED_FOOTER = "🚀 <b>Starting streak with FORCED footer...</b>"
FOOTER_COMPLETED = "✨ <b>Footer-only run completed!</b>"
RUN_FAILED = "❌ <b>Run failed:</b> {error}"

FILE_RECEIVED = "✅ <b>Received {file_name}</b>{extra_info} and updated successfully!"
FILE_NOT_RECOGNIZED = "ℹ️ <b>File not recognized.</b> Please send <code>cookies.json</code>, <code>users.txt</code>, or <code>messages.txt</code>."

DAILY_HEALTH_HEALTHY = "🌞 <b>Daily Health Check:</b> Cookies are ✅ HEALTHY."
DAILY_HEALTH_EXPIRED = "🚨 <b>Daily Health Check:</b> Cookies have ❌ EXPIRED! Please update <code>cookies.json</code>."

AUTO_STREAK_MISSING_FILES = "❌ <b>Auto-Streak Failed:</b> Missing <code>users.txt</code> or <code>messages.txt</code>!"
AUTO_STREAK_STARTING = "🚀 <b>Starting automated daily streak...</b>"
AUTO_STREAK_COMPLETED = "✨ <b>Automated streak run completed!</b>"
AUTO_STREAK_ERROR = "❌ <b>Auto-Streak Error:</b> {error}"

UNAUTHORIZED_ACCESS = "Unauthorized. You are not the owner of this bot."

# Messenger Strings (CLI & Logic)
def get_streak_prefix(date_str, days):
    return f"hôm nay là ngày {date_str} đã {days} ngày kể từ lúc mình thế chỗ Khanh trong lúc Khanh vắng mặt"

MSG_NO_COOKIES_FOUND = "[-] No cookies file found."
MSG_COOKIES_HEALTHY = "[+] Cookies are HEALTHY and valid."
MSG_COOKIES_EXPIRED = "[-] Cookies are EXPIRED or invalid."
MSG_WAITING_LOGIN = "[*] Waiting for user to login manually in the browser..."
MSG_LOGIN_INSTRUCTIONS = (
    "Please login to TikTok in the browser window.\n"
    "After you see your feed (the videos/home page), come back here.\n"
    "IMPORTANT: DO NOT CLOSE THE BROWSER WINDOW MANUALLY.\n"
    "Press Enter in this terminal ONLY AFTER you have successfully logged in."
)
MSG_STABILIZING = "[*] Waiting for session to stabilize..."
MSG_CAPTURING_COOKIES = "[*] Capturing cookies..."
MSG_CAPTURED_SUCCESS = "[*] Successfully captured {count} cookies."
MSG_COOKIES_SAVED = "[+] Cookies saved to {path}"
MSG_CAPTURE_FAILED = "[-] Failed to capture cookies: {error}"
MSG_STREAK_ALREADY_RUN = "[*] Streak already run today. Skipping."
MSG_STREAK_NO_COOKIES = "[-] No cookies found. Please run the login command first."

MSG_WEEKLY_INSTRUCTIONS = (
    "Mong bạn sẽ vẫn giữ chuỗi với Khanh nhé vì có chút việc bận nên bạn ý có lẽ sẽ không dùng tiktok thường xuyên\n"
    "nếu có chuỗi 30 hay 100,.. thì đăng str nhé, Mình sẽ nhắc thằng đấy vô tiktok để đăng chuỗi :))\n"
)

MSG_FOOTER_SENT = "[*] Footer message will be sent."
MSG_FOOTER_ONLY_SENT = "[*] Footer message will be sent (FOOTER ONLY)."

# TikTok Platform Strings
MSG_NAVIGATING_TIKTOK = "[*] Navigating to TikTok..."
MSG_INJECTING_COOKIES = "[*] Injecting {count} cookies..."
MSG_REFRESHING_COOKIES = "[*] Refreshing page to apply cookies..."
MSG_WAITING_VERIFICATION = "[*] Waiting for login verification..."
MSG_LOOKING_FOR_USER = "[*] Looking for {nickname} in message list..."
MSG_FOUND_WITH_SELECTOR = "[*] Found element with selector: {selector}"
MSG_CHAT_OPENED = "[*] Chat opened successfully."
MSG_USER_NOT_VISIBLE = "[*] {nickname} not visible, scrolling message list (attempt {attempt})..."
MSG_TYPING_TO = "[*] Typing message to {nickname}..."
MSG_SEND_BUTTON_NOT_FOUND = "[*] Send button not found, trying Enter key..."
MSG_SENT_TO = "[+] Message sent to {nickname}"
MSG_SEND_FAILED = "[-] Failed to send message to {nickname}: {error}"
MSG_NAVIGATING_MESSAGES = "[*] Navigating to messages page..."
MSG_PROCESSING_USER = "\n[*] Processing [{current}/{total}]: {nickname}"
MSG_SENDING_WEEKLY = "[*] Sending weekly instructions to {nickname}..."
MSG_SENDING_FOOTER_ONLY = "[*] Sending footer ONLY to {nickname}..."
