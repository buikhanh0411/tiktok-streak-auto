from typing import Any, List, Dict, Optional
import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from src.interfaces.contracts import IBrowserEngine

class PlaywrightEngine(IBrowserEngine):
    """Playwright implementation of IBrowserEngine (Async)"""

    def __init__(self):
        self._playwright_context_manager = None
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    async def launch(self, headless: bool = True) -> None:
        self._playwright_context_manager = async_playwright()
        self._playwright = await self._playwright_context_manager.start()
        self._browser = await self._playwright.chromium.launch(headless=headless)
        self._context = await self._browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        self._page = await self._context.new_page()

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def goto(self, url: str) -> None:
        if self._page:
            await self._page.goto(url)

    async def get_cookies(self) -> List[Dict[str, Any]]:
        return await self._context.cookies() if self._context else []

    async def set_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        if self._context:
            clean_cookies = []
            for c in cookies:
                clean_cookie = {
                    "name": str(c.get("name")),
                    "value": str(c.get("value")),
                    "domain": str(c.get("domain")),
                    "path": str(c.get("path", "/")),
                    "secure": bool(c.get("secure", False)),
                    "httpOnly": bool(c.get("httpOnly", False)),
                }
                # Handle expires
                expires = c.get("expires")
                if expires and expires > 0:
                    clean_cookie["expires"] = float(expires)
                
                # Handle sameSite
                ss = c.get("sameSite")
                if ss in ["Lax", "Strict", "None"]:
                    clean_cookie["sameSite"] = ss
                
                clean_cookies.append(clean_cookie)
            
            await self._context.add_cookies(clean_cookies)

    async def click(self, selector: str) -> None:
        if self._page:
            # Use locator to handle potential multiple elements
            # Pick the first one that is visible
            locator = self._page.locator(selector).first
            await locator.scroll_into_view_if_needed()
            await locator.click(force=True)

    async def type(self, selector: str, text: str) -> None:
        if self._page:
            locator = self._page.locator(selector).first
            await locator.scroll_into_view_if_needed()
            await locator.fill(text)

    async def press(self, selector: str, key: str) -> None:
        if self._page:
            locator = self._page.locator(selector).first
            await locator.press(key)

    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> None:
        if self._page:
            await self._page.wait_for_selector(selector, timeout=timeout)

    async def get_text(self, selector: str) -> str:
        if self._page:
            return await self._page.inner_text(selector)
        return ""

    async def get_url(self) -> str:
        if self._page:
            return self._page.url
        return ""

    async def wait_for_user_interaction(self, prompt: str) -> None:
        print(f"\n[!] {prompt}")
        print("[!] Press Enter in this terminal once you are ready to continue...")
        await asyncio.to_thread(input)
