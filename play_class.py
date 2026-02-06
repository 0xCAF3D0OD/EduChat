import asyncio
from tkinter.constants import PAGES
from typing import Any, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Playwright, Page

from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError, # ⏱️ Timeout
    Error,                 # 🔴 Erreur générale Playwright
)

def debug_logs(text: str):
    """Print debugging info"""
    print(f"DEBUG: - {text}", flush=True)

# 1. Define the class (the blueprint)
class Browser:
    # The constructor method to initialize new objects
    def __init__(self, browser_type):
        self.browser = browser_type

        self.page = None
        self.context = None
        self.response = []
        self.api_request_context = None

    async def handle_response(self, response: Any) -> Any:
        # Filtrer UNIQUEMENT les réponses importantes
        if "api" in response.url or "chat" in response.url or response.status >= 400:
            self.response.append({
                "url": response.url,
                "status": response.status,
                "ok": response.ok,
                "timestamp": datetime.now()
            })

    async def browser_new_page(self) -> Any:
        """
         Initialize a new browser context (new tab) with tracing enabled and attach a response listener.

         Returns a page navigated to WhatsApp Web (whatsapp login qrcode), or None if initialization fails.
         The response listener remains active for the lifetime of the page.
         """
        try:
            # create a new incognito browser context
            self.context = await self.browser.new_context()

            # Start recording a trace before performing actions. At the end, stop tracing and save it to a file.
            await self.context.tracing.start(
                screenshots=True,
                snapshots=True
            )

            # Creates a new page in a new browser context.
            # Closing this page will close the context as well.
            self.page = await self.context.new_page()

            # Emitted when a page issues a request.
            # The request object is read-only.
            # In order to intercept and mutate requests,
            self.page.on("response", self.handle_response)

            # https://playwright.dev/python/docs/api/class-page#page-goto
            await self.page.goto(
                "https://web.whatsapp.com",
                timeout=10000
            )
            return self.page

        except TimeoutError:
            print("❌ Timeout: WhatsApp Web n'a pas pu charger")
            return None

        except Error as e:
            print(f"❌ Playwright Error: {e}")
            return None

        except Exception as e:  # Fallback pour les autres erreurs
            print(f"❌ Erreur inconnue: {e}")
            return None

    def get_responses(self):
        return self.response

    def print_responses(self):
        for r in self.response:
            print(f"{r['status']} - {r['url']}")

    def get_context(self) -> Any:
        return self.context

    async def close_browser(self):
        await self.browser.close()

class Whatsapp:
    def __init__(self, page: Any, browser_instance: Browser):
        self.page = page
        self.browser = browser_instance

    async def take_screenshot(self, path: str) -> Optional[str]:
        """Take a screenshot of the QR code"""
        debug_logs("waiting for QR code...")
        qr_code = None
        try:
            qr_code = self.page.get_by_role(
                "img",
                name="Scan this QR code to link a"
            )
            await qr_code.wait_for()

        except PlaywrightTimeoutError:
            print("Timeout!")
            await self.browser.close_browser()

        debug_logs("screenshot...")
        await qr_code.screenshot(path=path)
        print(f"QR code: {qr_code}")

    async def get_locator(self, type_locator: str, locator: Any) -> Any:
        try:
            locator = self.page.get_by_role(type_locator, name=locator)
            await locator.wait_for(timeout=10000)
            return True

        except PlaywrightTimeoutError:
            await self.browser.close_browser()
            return False