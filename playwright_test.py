import asyncio
from typing import Optional
import re

from playwright.async_api import async_playwright, Playwright, Page, WebSocketRoute
from utils import debug_logs, handle_playwright_errors
from play_class import Browser, Whatsapp
from playwright.async_api import (
    Error,
    TimeoutError,
)
from websocket_playwright import r_websocket

RETRY_COUNT = 5

# Patterns possibles
PATTERNS = ["Search or start a new chat", "Nouvelle discussion", "new chat"]

# Créer un regex avec | (OR) à partir des patterns
PATTERN_REGEX = re.compile("|".join(PATTERNS), re.IGNORECASE)

@handle_playwright_errors
async def login_whatsapp_session(firefox: Browser, whatsapp: Whatsapp) -> None:
    await whatsapp.take_screenshot("./images/whatsapp.png")
    firefox.print_responses()
    button = whatsapp.page.get_by_role("button", name=PATTERN_REGEX)
    await button.wait_for()
    await (whatsapp.page.screenshot(path="./images/page.png"))

@handle_playwright_errors
async def launch_whatsapp(firefox: Browser) -> Optional[Whatsapp]:
    # get whatsapp page and take the screenshot of the QR code
    for attempt in range(RETRY_COUNT):  # attempt = 0, 1, 2, 3, 4
        try:
            # ÉTAPE 2 : Créer une page WhatsApp
            page = await firefox.get_or_create_whatsapp_page() # ✅ Singleton -> Create Whatsapp page
            if not page:
                debug_logs(f"❌ Page is None - Attempt {attempt + 1}/{RETRY_COUNT}")
                continue

            await r_websocket(page)

            whatsapp = await Whatsapp.get_or_create(page, firefox) # ✅ Singleton -> Create Whatsapp instance
            await whatsapp.take_screenshot("./images/whatsapp.png")
            firefox.print_responses()
            button = whatsapp.page.get_by_role("button", name=PATTERN_REGEX)

            await button.wait_for()

            await (whatsapp.page.screenshot(path="./images/page.png"))
            return whatsapp
        except TimeoutError:
            debug_logs(f"❌ Screenshot timeout - Attempt {attempt + 1}/{RETRY_COUNT}")
            if attempt < RETRY_COUNT - 1:
                debug_logs("Reloading page...")
                await page.reload()  # ← Rafraîchir et réessayer
            else:
                raise  # ← Dernier essai, lever l'exception
        except Exception as e:
            debug_logs(f"❌ Erreur: {e}")
            raise
    return None

async def run_websocket(playwright: Playwright) -> None:
    firefox = await Browser.get_or_create_browser_instance(playwright)

    try:
        whatsapp = await launch_whatsapp(firefox)
        if whatsapp:
            button = whatsapp.page.get_by_role("button", name=PATTERN_REGEX)
            await button.wait_for()
            await (whatsapp.page.screenshot(path="./images/page.png"))

    except OSError as e:
        debug_logs(f"❌ Firefox not found: {e}")
        debug_logs("stop tracing...")
        await firefox.context.tracing.stop(path="tracing.zip")
        await firefox.close_browser()
    except Exception as e:
        debug_logs(f"❌ Firefox has not been launched... {e}")
        debug_logs("stop tracing...")
        await firefox.context.tracing.stop(path="tracing.zip")
        await firefox.close_browser()
    except TimeoutError:
        debug_logs("❌ Firefox launch timeout")
        debug_logs("stop tracing...")
        await firefox.context.tracing.stop(path="tracing.zip")
        await firefox.close_browser()
    except Error as e:
        debug_logs(f"❌ Playwright error: {e}")
        debug_logs("stop tracing...")
        await firefox.context.tracing.stop(path="tracing.zip")
        await firefox.close_browser()

async def main():
    async with async_playwright() as playwright:
        await run_websocket(playwright)

asyncio.run(main())

# import asyncio
# from playwright.async_api import async_playwright, Playwright
#
#
# async def run(playwright: Playwright):
#     context = await playwright.request.new_context()
#
#     response = await context.get("https://api.github.com/users/microsoft")
#
#     print(f"Status: {response.status}")
#     print(f"Content-Type: {response.headers.get('content-type')}")
#
#     assert response.ok
#     assert response.status == 200
#
#     json_data = await response.json()
#     print(f"User login: {json_data['login']}")
#     print(f"User name: {json_data['name']}")
