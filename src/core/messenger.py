import json
import os
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from src.interfaces.contracts import IBrowserEngine, ISocialPlatform
from src.core import config, messages

# Global start date for the streak counter
START_DATE = config.STREAK_START_DATE


class Messenger:
    """Orchestrator for browser automation and social platforms (Async)"""

    def __init__(
        self,
        engine: IBrowserEngine,
        platform: ISocialPlatform,
        cookie_file: str = config.COOKIES_FILE,
        state_file: str = config.STATE_FILE,
    ):
        self.engine = engine
        self.platform = platform
        self.cookie_file = cookie_file
        self.state_file = state_file
        self._state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {
            "last_footer_sent": "2000-01-01T00:00:00",
            "last_streak_run": "2000-01-01",
        }

    def _save_state(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self._state, f)

    def _should_run_streak(self) -> bool:
        """Checks if a streak has already been run today."""
        last_run_str = self._state.get("last_streak_run", "2000-01-01")
        # Ensure we only compare the date part
        last_run_date = last_run_str.split("T")[0]
        today_date = datetime.now().strftime("%Y-%m-%d")
        return last_run_date != today_date

    def _get_streak_prefix(self) -> str:
        """Calculates the streak prefix with current date and days since START_DATE"""
        now = datetime.now()
        delta = now.date() - START_DATE.date()
        days = max(0, delta.days)
        date_str = now.strftime("%d-%m-%Y")
        return messages.get_streak_prefix(date_str, days)

    def _should_send_footer(self) -> bool:
        """Determines if the long footer should be sent (approx once a week)"""
        last_sent = datetime.fromisoformat(
            self._state.get("last_footer_sent", "2000-01-01T00:00:00")
        )
        now = datetime.now()

        # If it's been more than 7 days, we should send it
        if (now - last_sent) >= timedelta(days=7):
            return True

        return False

    async def check_cookies_health(self) -> bool:
        """Verify if the saved cookies are still valid without running a full streak"""
        if not os.path.exists(self.cookie_file):
            print(messages.MSG_NO_COOKIES_FOUND)
            return False

        with open(self.cookie_file, "r") as f:
            cookies = json.load(f)

        await self.engine.launch(headless=True)  # Headless is fine for check
        try:
            success = await self.platform.login_with_cookies(cookies)
            if success:
                print(messages.MSG_COOKIES_HEALTHY)
            else:
                print(messages.MSG_COOKIES_EXPIRED)
            return success
        finally:
            await self.engine.close()

    async def login_manually(self) -> None:
        """Helper to let user login and save cookies"""
        await self.engine.launch(headless=False)
        await self.engine.goto("https://www.tiktok.com/login")
        print(messages.MSG_WAITING_LOGIN)

        await self.engine.wait_for_user_interaction(messages.MSG_LOGIN_INSTRUCTIONS)

        # Give a small buffer for last minute cookies to settle
        print(messages.MSG_STABILIZING)
        await asyncio.sleep(2)

        print(messages.MSG_CAPTURING_COOKIES)
        try:
            cookies = await self.engine.get_cookies()
            print(messages.MSG_CAPTURED_SUCCESS.format(count=len(cookies)))

            os.makedirs(os.path.dirname(self.cookie_file), exist_ok=True)
            with open(self.cookie_file, "w") as f:
                json.dump(cookies, f)

            print(messages.MSG_COOKIES_SAVED.format(path=self.cookie_file))
        except Exception as e:
            print(messages.MSG_CAPTURE_FAILED.format(error=str(e)))
        finally:
            await self.engine.close()

    async def run_streak(
        self,
        nicknames: List[str],
        messages_list: List[str],
        force_footer: bool = False,
        headless: bool = True,
        force: bool = False,
        footer_only: bool = False,
    ) -> None:
        """Load cookies and send randomized messages with a streak prefix (and optional weekly footer)"""
        if not force and not self._should_run_streak():
            print(messages.MSG_STREAK_ALREADY_RUN)
            return

        if not os.path.exists(self.cookie_file):
            print(messages.MSG_STREAK_NO_COOKIES)
            return

        with open(self.cookie_file, "r") as f:
            cookies = json.load(f)

        prefix = self._get_streak_prefix()

        # Determine if we should send the second message (footer)
        include_footer = footer_only or force_footer or self._should_send_footer()

        footer_msg = messages.MSG_WEEKLY_INSTRUCTIONS

        if not footer_only:
            print(f"[*] Streak Prefix: {prefix}")
        if include_footer:
            print(
                messages.MSG_FOOTER_ONLY_SENT if footer_only else messages.MSG_FOOTER_SENT
            )

        await self.engine.launch(headless=headless)
        try:
            if await self.platform.login_with_cookies(cookies):
                print(messages.MSG_NAVIGATING_MESSAGES)
                await self.engine.goto(config.TIKTOK_MESSAGES_URL)
                await asyncio.sleep(8)

                total = len(nicknames)
                for i, nickname in enumerate(nicknames, 1):
                    print(messages.MSG_PROCESSING_USER.format(current=i, total=total, nickname=nickname))

                    success = True
                    # Only send streak if NOT in footer_only mode
                    if not footer_only:
                        # Pick a random message from the list
                        base_msg = random.choice(messages_list)
                        first_message = f"{prefix}\n\n{base_msg}"

                        # Send 1st message (Streak)
                        success = await self.platform.send_message(
                            nickname, first_message
                        )

                    # Send footer if it's time or forced
                    if success and include_footer:
                        if not footer_only:
                            print(messages.MSG_SENDING_WEEKLY.format(nickname=nickname))
                            await asyncio.sleep(random.uniform(1, 3))
                        else:
                            print(messages.MSG_SENDING_FOOTER_ONLY.format(nickname=nickname))

                        await self.platform.send_message(nickname, footer_msg)

                    if i < total:
                        wait_time = random.uniform(3, 7)
                        print(f"[*] Waiting {wait_time:.1f}s before next user...")
                        await asyncio.sleep(wait_time)

                # Update state if we sent the footer
                if include_footer and not footer_only:
                    # Only update the weekly timer if it was a normal run with footer
                    # Or should we update it anyway? Let's say manual footer ONLY doesn't reset the 7-day timer
                    self._state["last_footer_sent"] = datetime.now().isoformat()

                # Update last run date (only for normal streak runs)
                if not footer_only:
                    self._state["last_streak_run"] = datetime.now().strftime("%Y-%m-%d")

                self._save_state()
            else:
                print("[-] Login failed with saved cookies.")
        finally:
            await self.engine.close()
