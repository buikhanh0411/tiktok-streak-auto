from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional

class IBrowserEngine(ABC):
    """Interface for browser automation engines (e.g., Playwright, nodriver)"""

    @abstractmethod
    async def launch(self, headless: bool = True) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def goto(self, url: str) -> None:
        pass

    @abstractmethod
    async def get_cookies(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def set_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        pass

    @abstractmethod
    async def click(self, selector: str) -> None:
        pass

    @abstractmethod
    async def type(self, selector: str, text: str) -> None:
        pass

    @abstractmethod
    async def press(self, selector: str, key: str) -> None:
        pass

    @abstractmethod
    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> None:
        pass

    @abstractmethod
    async def get_text(self, selector: str) -> str:
        pass

    @abstractmethod
    async def get_url(self) -> str:
        pass

    @abstractmethod
    async def wait_for_user_interaction(self, prompt: str) -> None:
        pass

class ISocialPlatform(ABC):
    """Interface for social media platforms (e.g., TikTok, Instagram)"""

    @abstractmethod
    async def login_with_cookies(self, cookies: List[Dict[str, Any]]) -> bool:
        pass

    @abstractmethod
    async def is_logged_in(self) -> bool:
        pass

    @abstractmethod
    async def send_message(self, nickname: str, message: str) -> bool:
        pass

    @abstractmethod
    async def find_user_by_nickname(self, nickname: str) -> bool:
        pass
