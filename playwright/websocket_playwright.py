import asyncio
from typing import Optional, Union
from playwright.async_api import WebSocketRoute, Page

def message_handler(ws: WebSocketRoute, message: Union[str, bytes]):
  if message == "request":
    ws.send("response")

def handler(ws: WebSocketRoute):
  ws.on_message(lambda message: message_handler(ws, message))

async def r_websocket(page: Page):
    await page.route_web_socket("/ws", handler)
