import nodriver as uc
import asyncio
from typing import Any, List, Dict, Optional
from src.interfaces.contracts import IBrowserEngine
from nodriver.cdp import network

# Monkeypatch nodriver's Cookie.from_json to handle missing 'sameParty' field
# Modern Chrome versions have deprecated/removed sameParty, but nodriver's 
# generated CDP code still expects it.
_original_from_json = network.Cookie.from_json

def _lenient_from_json(json: dict) -> network.Cookie:
    # Ensure all required fields for network.Cookie.from_json are present
    defaults = {
        "sameParty": False,
        "sourceScheme": "Unset",
        "sourcePort": -1,
        "priority": "Medium",
        "sameSite": "None"
    }
    for key, value in defaults.items():
        if key not in json:
            json[key] = value
    
    # Map string priority/sameSite to enums if necessary, but from_json usually handles strings
    return _original_from_json(json)

network.Cookie.from_json = _lenient_from_json

class NodriverEngine(IBrowserEngine):
    """Nodriver implementation of IBrowserEngine to bypass 'browser not secure'"""

    def __init__(self):
        self._browser = None
        self._page = None

    async def launch(self, headless: bool = True) -> None:
        # nodriver uses 'browser' as the main entry point
        # it starts a browser instance and usually opens a tab by default
        self._browser = await uc.start(headless=headless)
        self._page = self._browser.main_tab

    async def close(self) -> None:
        if self._browser:
            try:
                # nodriver stop is usually not awaited in some versions,
                # but we'll try to await it to be safe or catch errors
                await self._browser.stop()
            except:
                # If it's already closed or doesn't need await
                pass
            self._browser = None
            self._page = None

    async def goto(self, url: str) -> None:
        if self._page:
            await self._page.get(url)

    async def get_cookies(self) -> List[Dict[str, Any]]:
        if not self._browser:
            return []
        
        try:
            cookies = await self._browser.cookies.get_all()
            clean_cookies = []
            for c in cookies:
                # Manually build dictionary to ensure compatibility
                # We store with camelCase to match Playwright/common standards
                cookie = {
                    "name": c.name,
                    "value": c.value,
                    "domain": c.domain,
                    "path": c.path,
                    "expires": getattr(c, 'expires', -1),
                    "httpOnly": getattr(c, 'http_only', False),
                    "secure": getattr(c, 'secure', False),
                    "sameSite": str(c.same_site.value) if hasattr(c, 'same_site') and hasattr(c.same_site, 'value') else "None"
                }
                clean_cookies.append(cookie)
            return clean_cookies
        except Exception as e:
            return []

    async def set_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        if self._browser:
            from nodriver import cdp
            
            cookie_params = []
            for c in cookies:
                # Map our stored format to CookieParam expected by nodriver/CDP
                # We use snake_case for http_only as required by nodriver's generated code
                param = cdp.network.CookieParam(
                    name=c.get("name"),
                    value=c.get("value"),
                    domain=c.get("domain"),
                    path=c.get("path", "/"),
                    secure=c.get("secure", False),
                    http_only=c.get("httpOnly", False),
                    expires=c.get("expires", -1),
                    same_site=cdp.network.CookieSameSite(c.get("sameSite")) if c.get("sameSite") in ["Lax", "Strict", "None"] else cdp.network.CookieSameSite.NONE
                )
                cookie_params.append(param)
            
            await self._browser.cookies.set_all(cookie_params)

    async def _find_element(self, selector: str, timeout: int = 30000):
        if selector.startswith("text="):
            text = selector[len("text="):].strip("'\"")
            return await self._page.find(text, best_match=True)
        else:
            return await self._page.select(selector)

    async def click(self, selector: str) -> None:
        if self._page:
            element = await self._find_element(selector)
            if element:
                await element.click()

    async def type(self, selector: str, text: str) -> None:
        if self._page:
            element = await self._find_element(selector)
            if element:
                await element.send_keys(text)

    async def press(self, selector: str, key: str) -> None:
        if self._page:
            element = await self._find_element(selector)
            if element:
                # In nodriver, send_keys can be used for keys
                await element.send_keys(key)

    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> None:
        if self._page:
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < (timeout / 1000):
                element = await self._find_element(selector)
                if element:
                    return
                await asyncio.sleep(0.5)
            raise TimeoutError(f"Selector {selector} not found within {timeout}ms")

    async def get_text(self, selector: str) -> str:
        if self._page:
            element = await self._page.select(selector)
            return element.text if element else ""
        return ""

    async def get_url(self) -> str:
        if self._page:
            return self._page.url
        return ""

    async def wait_for_user_interaction(self, prompt: str) -> None:
        print(f"\n[!] {prompt}")
        print("[!] Press Enter in this terminal once you are ready to continue...")
        await asyncio.to_thread(input)
