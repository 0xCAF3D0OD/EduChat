import asyncio
from tkinter.constants import PAGES
from typing import Any
from playwright.async_api import async_playwright, Playwright, Page

def debug_logs(text: str):
    """Print debugging info"""
    print(f"DEBUG: - {text}", flush=True)

async def hide_whatsapp_logo(page: Page) -> None:
    """Remove the Whatsapp logo from the QR code"""
    await page.evaluate('''
        () = > {
            const
        logo = document.querySelector('div._akaz');
        if (logo) logo.style.visibility = 'hidden';
        }
    ''')

async def get_screenshot(page: Page) -> None:
    """Take a screenshot of the QR code"""
    debug_logs("waiting for QR code...")
    await page.wait_for_selector('canvas[aria-label*="QR"][role="img"]')

    debug_logs("QR code locator...")
    qr_code = page.locator('canvas[aria-label*="QR"][role="img"]')

    debug_logs("screenshot...")
    await qr_code.screenshot(path="./images/qr.png")

async def run_websocket(playwright: Playwright) -> None:
    """Run the WebSocket server"""
    firefox = await playwright.firefox.launch()

    # create a new incognito browser context
    context = await firefox.new_context()

    await context.tracing.start(screenshots=True, snapshots=True)

    # create a new page inside context.
    page = await context.new_page()

    debug_logs("Goto Whatsapp web...")
    await page.goto("https://web.whatsapp.com/")

    debug_logs("get QR code screenshot...")
    await get_screenshot(page)

    debug_logs("stop tracing...")
    await context.tracing.stop(path="tracing.zip")

    # dispose context once it is no longer needed.
    await context.close()
    await firefox.close()

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
