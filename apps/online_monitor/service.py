import os
import json
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

from core.config import settings
from discord_notifier.notifier import DiscordNotifier
from apps.online_monitor.models import Player

ONLINE_URL = f"{settings.BASE_URL}/character/online"
CHARACTER_BASE_URL = f"{settings.BASE_URL}/character/view/"
CACHE_FILE = "data/last_online.json"

def load_list_online() -> set[str]:
    if not os.path.exists(CACHE_FILE):
        return set()
    with open(CACHE_FILE, "r") as f:
        return set(json.load(f))
    
def save_last_online(player_names: set[str]):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(player_names), f, ident=2)

def format_discord_message(player: Player) -> str:
    hora = datetime.now().strftime("%H:%M:%S")
    if player.guild == "Red Sky":
        return f"[FRIEND-{hora}] Acabou de logar: {player.name} (Level {player.level})"
    elif player.guild == "Carteira Assinada":
        return f"[HUNTED-{hora}] Acabou de logar: {player.name} (Level {player.level})"
    return ""  # Ignora guilds irrelevantes

async def fetch_html(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
        
def parse_online_players(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table tr")
    player_names = []
    for row in rows:
        link = row.find("a")
        if link:
            name = link.text.strip()
            player_names.append(name)
    return player_names