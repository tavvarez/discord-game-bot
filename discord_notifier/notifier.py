import aiohttp
from core.config import settings

import aiohttp

async def send_discord_message(content: str, webhook_url: str, color: int = 0x000000):
    if not webhook_url:
        print("[ERRO] Webhook do Discord não configurado.")
        return

    payload = {
        "embeds": [
            {
                "description": content,
                "color": color
            }
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as resp:
                if resp.status != 204:  # Discord Webhook responde 204 No Content
                    body = await resp.text()
                    print(f"[ERRO] Falha ao enviar webhook. Status {resp.status}: {body}")
    except Exception as e:
        print(f"[ERRO] Exceção ao enviar webhook: {e}")

