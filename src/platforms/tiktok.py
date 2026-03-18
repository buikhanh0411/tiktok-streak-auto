import asyncio
import random
from typing import List, Dict, Any
from src.interfaces.contracts import ISocialPlatform, IBrowserEngine
from src.core import config, messages

class TikTokPlatform(ISocialPlatform):
    """TikTok implementation of ISocialPlatform (Async)"""

    BASE_URL = config.TIKTOK_BASE_URL
    MESSAGES_URL = config.TIKTOK_MESSAGES_URL

    def __init__(self, engine: IBrowserEngine):
        self.engine = engine

    async def is_logged_in(self) -> bool:
        """Check if current session is logged in by verifying URL and presence of login button"""
        url = await self.engine.get_url()
        if "tiktok.com/login" in url:
            return False

        # Check if login button is visible
        try:
            # TikTok login button often has data-e2e="nav-login-button"
            await self.engine.wait_for_selector('[data-e2e="nav-login-button"]', timeout=3000)
            return False
        except:
            # If login button is not found, assume we are logged in or on a neutral page
            # To be sure, check for profile or upload icons
            try:
                await self.engine.wait_for_selector('[data-e2e="profile-icon"], [data-e2e="upload-icon"]', timeout=3000)
                return True
            except:
                # If neither found, just check URL again
                return "tiktok.com/login" not in url

    async def login_with_cookies(self, cookies: List[Dict[str, Any]]) -> bool:
        """Inject cookies and verify login state"""
        print(messages.MSG_NAVIGATING_TIKTOK)
        await self.engine.goto(self.BASE_URL)
        
        print(messages.MSG_INJECTING_COOKIES.format(count=len(cookies)))
        await self.engine.set_cookies(cookies)
        await asyncio.sleep(2) # Buffer to settle cookies
        
        print(messages.MSG_REFRESHING_COOKIES)
        await self.engine.goto(self.BASE_URL)
        
        # Wait for the feed or a profile indicator to appear
        print(messages.MSG_WAITING_VERIFICATION)
        await asyncio.sleep(5)
        return await self.is_logged_in()


    async def send_message(self, nickname: str, message: str) -> bool:
        """Find user by scrolling the inbox list and send message"""
        try:
            print(messages.MSG_LOOKING_FOR_USER.format(nickname=nickname))
            
            # Using specific PInfoNickname class provided by the user
            selectors = [
                f'p[class*="PInfoNickname"]:has-text("{nickname}")',
                f'p:has-text("{nickname}")',
                f'text="{nickname}"'
            ]
            
            # Selector for the scrollable inbox container
            # User provided: css-1gcu5ek-7937d88b--DivDrawerContainer
            inbox_container_selectors = [
                'div[class*="DivDrawerContainer"]',
                '[data-e2e="inbox-list"]',
                '.e1m74s5b0' # Common class for the sidebar
            ]
            
            inbox_selector = None
            for s in inbox_container_selectors:
                try:
                    await self.engine.wait_for_selector(s, timeout=2000)
                    inbox_selector = s
                    break
                except:
                    continue

            element_found = False
            # If the user is far down, TikTok might use a virtual list
            for attempt in range(20): # Increased attempts for long lists
                for selector in selectors:
                    try:
                        await self.engine.wait_for_selector(selector, timeout=1000)
                        print(messages.MSG_FOUND_WITH_SELECTOR.format(selector=selector))
                        
                        # Click the user
                        await self.engine.click(selector)
                        
                        # Verification: see if chat opens
                        await asyncio.sleep(2)
                        input_selector = 'div[role="textbox"]'
                        try:
                            await self.engine.wait_for_selector(input_selector, timeout=2000)
                            element_found = True
                            print(messages.MSG_CHAT_OPENED)
                            break
                        except:
                            continue
                    except:
                        continue
                
                if element_found:
                    break
                
                # If not found, scroll the container
                print(messages.MSG_USER_NOT_VISIBLE.format(nickname=nickname, attempt=attempt+1))
                try:
                    # Hover first to ensure focus, then press PageDown
                    if inbox_selector:
                        # We use press on the container
                        await self.engine.press(inbox_selector, "PageDown")
                    else:
                        await self.engine.press("body", "PageDown")
                except:
                    await self.engine.press("body", "PageDown")
                
                await asyncio.sleep(1.5)

            if not element_found:
                raise Exception(f"Could not find or open chat with {nickname} after scrolling.")
            
            # Find the message input box
            input_selector = 'div[role="textbox"]'
            await self.engine.wait_for_selector(input_selector, timeout=5000)
            print(messages.MSG_TYPING_TO.format(nickname=nickname))
            await self.engine.type(input_selector, message)
            
            # Send
            await asyncio.sleep(1)
            try:
                send_button_selectors = [
                    'svg[data-e2e="message-send"]',
                    'button[data-e2e="message-send-button"]',
                    '[aria-label="Send message"]'
                ]
                
                send_clicked = False
                for btn_selector in send_button_selectors:
                    try:
                        await self.engine.wait_for_selector(btn_selector, timeout=1500)
                        await self.engine.click(btn_selector)
                        send_clicked = True
                        break
                    except:
                        continue
                
                if not send_clicked:
                    print(messages.MSG_SEND_BUTTON_NOT_FOUND)
                    await self.engine.press(input_selector, "Enter")
            except:
                await self.engine.press(input_selector, "Enter")
            
            print(messages.MSG_SENT_TO.format(nickname=nickname))
            return True
        except Exception as e:
            print(messages.MSG_SEND_FAILED.format(nickname=nickname, error=str(e)))
            return False

    async def find_user_by_nickname(self, nickname: str) -> bool:
        """Helper to find if a user exists in the message list"""
        return False
