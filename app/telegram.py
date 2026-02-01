import os
import logging
import httpx

logger = logging.getLogger("uptime.telegram")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_telegram(text: str) -> None:
    """Send a Telegram message if token/chat_id are configured."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(url, data=data)
            r.raise_for_status()
    except Exception as e:
        # Never crash the service if Telegram is down / misconfigured
        logger.warning("telegram send failed", extra={"extra": {"error": str(e)}})
