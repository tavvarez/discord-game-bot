import os
import json
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
from core.config import settings
from discord_notifier.notifier import send_discord_message
from apps.online_monitor.models import Player

ONLINE_URL = f"{settings.BASE_URL}/character/online"
CHARACTER_BASE_URL = f"{settings.BASE_URL}/character/view/"
CACHE_FILE = "data/last_levels.json"

semaphore = asyncio.Semaphore(10)  # Limita a 10 requisições simultâneas

def load_last_levels() -> dict:
    if not os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "w") as f:
            json.dump({}, f)
        return {}
    with open(CACHE_FILE, "r") as f:
        return json.load(f)


def save_last_levels(data: dict):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def parse_online_players(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table tr")
    names = []
    for row in rows:
        link = row.find("a")
        if link:
            names.append(link.text.strip())
    return names


async def fetch_html(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


async def get_player_details(name: str) -> Player | None:
    async with semaphore:
        url = f"{CHARACTER_BASE_URL}{name.replace(' ', '%20')}"
        html = await fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        level = 0
        vocation = ""
        guild = ""

        rows = soup.select("table tr")
        for row in rows:
            tds = row.find_all("td")
            if len(tds) != 2:
                continue
            label = tds[0].text.strip()
            value = tds[1].text.strip()
            if label == "Level:":
                level = int(value)
            elif label == "Vocação:":
                vocation = value
            elif label == "Guild membership":
                if "Red Sky" in value:
                    guild = "Red Sky"
                elif "Alta Cupula" in value:
                    guild = "Alta Cupula"

        if level < 400:
            return None

        return Player(name=name, vocation=vocation, level=level, guild=guild)


async def monitor_level_ups():
    html = await fetch_html(ONLINE_URL)
    online_names = parse_online_players(html)
    last_levels = load_last_levels()
    updated = False

    tasks = [get_player_details(name) for name in online_names]
    players = await asyncio.gather(*tasks)

    for player in players:
        if player is None:
            continue

        try:
            last_level = last_levels.get(player.name)

            if last_level is None:
                last_levels[player.name] = player.level
                continue

            if player.level > last_level:
                hora = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%H:%M:%S")

                if player.guild == "Red Sky":
                    msg = f"🆙 - {hora} [**FRIEND**]  **{player.name}** upou para o level **{player.level}** ( {player.vocation} )"
                    color = 0x00ff00
                elif player.guild == "Alta Cupula":
                    msg = f"🆙 - {hora} [**ENEMY**]  **{player.name}** upou para o level **{player.level}** ( {player.vocation} )"
                    color = 0xff0000
                else:
                    continue

                await send_discord_message(msg, settings.DISCORD_WEBHOOK_URL_LEVEL_UP, color=color)
                last_levels[player.name] = player.level
                updated = True
        except Exception as e:
            print(f"[ERRO] monitor_level_ups({player.name}): {e}")

    if updated:
        save_last_levels(last_levels)

