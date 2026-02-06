import asyncio
from typing import Optional
import re

from playwright.async_api import async_playwright, Playwright, Page

from playwright.async_api import (
    Error,
    TimeoutError,
)

from play_class import Browser, Whatsapp, debug_logs

# Patterns possibles
PATTERNS = ["Search or start a new chat", "Nouvelle discussion", "new chat"]

# Créer un regex avec | (OR) à partir des patterns
PATTERN_REGEX = re.compile("|".join(PATTERNS), re.IGNORECASE)

async def launch_browser(playwright: Playwright) -> Optional[Browser]:
    try:
        # launch firefox browser, initialise browser class
        firefox = await playwright.firefox.launch()
        b1 = Browser(firefox)
        debug_logs("Firefox has been launched...")
        return b1
    except TimeoutError:
        debug_logs("❌ Firefox launch timeout")
        return None
    except Error as e:
        debug_logs(f"❌ Playwright error: {e}")
        return None
    except OSError as e:  # Firefox not found
        debug_logs(f"❌ Firefox not found: {e}")
        return None
    except Exception as e:
        debug_logs(f"Firefox has not been launched... {e}")
        return None

async def launch_whatsapp(firefox: Browser) -> Optional[Whatsapp]:
    try:
        # get whatsapp page and take the screenshot of the QR code
        page = await firefox.browser_new_page()
        if page:
            whatsapp = Whatsapp(page, firefox)
            await whatsapp.take_screenshot("./images/whatsapp.png")
            firefox.print_responses()
            return whatsapp

    except TimeoutError:
        debug_logs("❌ Screenshot timeout")
    except Error as e:
        debug_logs(f"❌ Playwright error: {e}")

async def run_websocket(playwright: Playwright) -> None:
    firefox = await launch_browser(playwright)
    whatsapp = await launch_whatsapp(firefox)
    try:
        if whatsapp:
            button = whatsapp.page.get_by_role("button", name=PATTERN_REGEX)
            await button.wait_for()

            await (whatsapp.page.screenshot(path="./images/page.png"))

    except TimeoutError:
        debug_logs("❌ Firefox launch timeout")
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
