from functools import wraps
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError, # ⏱️ Timeout
    Error,                 # 🔴 Erreur générale Playwright
)

def debug_logs(text: str):
    """Print debugging info"""
    print(f"DEBUG: - {text}", flush=True)

def handle_playwright_errors(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except OSError as e:
            debug_logs(f"❌ OS error in {fn.__name__} with {e}")
            return None
        except Exception as e:
            debug_logs(f"Error in {fn.__name__} with {e}")
            return None
        except PlaywrightTimeoutError:
            debug_logs(f"❌ {fn.__name__} timeout")
            return None
        except Error as e:
            debug_logs(f"❌ Playwright error: {e}")
            return None
    return wrapper