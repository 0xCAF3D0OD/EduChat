import asyncio
from typing import Any, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Playwright, Page
from utils import debug_logs, handle_playwright_errors
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError, # ⏱️ Timeout
    Error,                 # 🔴 Erreur générale Playwright
)

def debug_logs(text: str):
    """Print debugging info"""
    print(f"DEBUG: - {text}", flush=True)

class Browser:
    _instance: Optional['Browser'] = None

    def __init__(self, browser_type):
        self.browser = browser_type
        self.context = None
        self.response = []

    @classmethod
    async def _check_if_existant_browser_instance(cls) -> bool:
        try:
            print(f"cls instance... equal to {cls._instance}")
            if cls._instance and cls._instance.browser.is_connected():
                debug_logs("Reuse of existing browser instance")
                return True
        except Exception:
            cls._instance = None
        return False

    @classmethod
    @handle_playwright_errors
    async def _create_new_browser_instance(cls, playwright: Playwright) -> Any:
        # Utiliser l'instance passée en paramètre
        print(f"1 cls instance... equal to {cls._instance}")

        firefox = await playwright.firefox.launch()
        cls._instance = cls(firefox)
        debug_logs("Browser has been launched...")

        print(f"2 cls instance... equal to {cls._instance}")
        return cls._instance

    @classmethod
    async def get_or_create_browser_instance(cls, playwright: Playwright) -> Optional['Browser']:
        """Obtain or create a new browser instance"""
        # Vérifier si une instance existe déjà
        if await cls._check_if_existant_browser_instance():
            return cls._instance
        return await cls._create_new_browser_instance(playwright)

    async def handle_response(self, response: Any) -> Any:
        # Filtrer UNIQUEMENT les réponses importantes
        if "api" in response.url or "chat" in response.url or response.status >= 400:
            self.response.append({
                "url": response.url,
                "status": response.status,
                "ok": response.ok,
                "timestamp": datetime.now()
            })

    async def new_context(self) -> Any:
        """Create a new browser context"""
        # create a new incognito browser context
        self.context = await self.browser.new_context()

        # Start recording a trace before performing actions. At the end, stop tracing and save it to a file.
        await self.context.tracing.start(
            screenshots=True,
            snapshots=True
        )

    async def new_page(self) -> Page:
        """Create a new Browser page"""
        # Creates a new page in a new browser context.
        # Closing this page will close the context as well.
        page = await self.context.new_page()

        # Emitted when a page issues a request.
        # The request object is read-only.
        # In order to intercept and mutate requests,
        page.on("response", self.handle_response)
        return page

    @handle_playwright_errors
    async def init_whatsapp_page(self) -> Any:
        """
         Initialize a new browser context (new tab) with tracing enabled and attach a response listener.

         Returns a page navigated to WhatsApp Web (whatsapp login qrcode), or None if initialization fails.
         The response listener remains active for the lifetime of the page.
         """
        await self.new_context()
        page = await self.new_page()

        # https://playwright.dev/python/docs/api/class-page#page-goto
        await page.goto(
            "https://web.whatsapp.com",
            timeout=10000
        )
        return page

    def get_responses(self):
        return self.response

    def print_responses(self):
        for r in self.response:
            print(f"{r['status']} - {r['url']}")

    def get_context(self) -> Any:
        return self.context

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
        self.__class__._instance = None
#end of Browser

class Whatsapp:
    def __init__(self, page: Any, browser_instance: Browser):
        self.page = page
        self.browser = browser_instance

    @handle_playwright_errors
    async def take_screenshot(self, path: str) -> Optional[str]:
        """Take a screenshot of the QR code"""
        debug_logs("waiting for QR code...")
        qr_code = self.page.get_by_role(
            "img",
            name="Scan this QR code to link a"
        )
        await qr_code.wait_for()

        debug_logs("screenshot...")
        await qr_code.screenshot(path=path)
        print(f"QR code: {qr_code}")

    @handle_playwright_errors
    async def get_locator(self, type_locator: str, locator: Any) -> Any:
        locator = self.page.get_by_role(type_locator, name=locator)
        await locator.wait_for(timeout=10000)
        return True
#end of Whatsapp