import os
import json
import aiohttp
from bs4 import BeautifulSoup
from core.config import settings
from apps.deaths_monitor.models import DeathRecord
from discord_notifier.notifier import send_discord_message



DATA_FILE = "data/last_deaths.json"
DEATHS_URL = f"{settings.BASE_URL}/p/v/deaths"

async def fetch_deaths_html():
    async with aiohttp.ClientSession() as session:
        async with session.get(DEATHS_URL) as response:
            return await response.text()

def parse_deaths(html: str) -> list[DeathRecord]:
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tr.highlight")

    deaths = []
    for row in rows:
        tds = row.find_all("td")
        if len(tds) != 2:
            continue
        datetime = tds[0].text.strip()
        description = tds[1].text.strip()
        deaths.append(DeathRecord(datetime=datetime, description=description))
    return deaths

def load_last_deaths() -> set[str]:
    if not os.path.exists(DATA_FILE):
        return set()
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        return set(data)

def save_last_deaths(death_keys: set[str]):
    with open(DATA_FILE, "w") as f:
        json.dump(list(death_keys), f, indent=2)

def generate_death_key(death: DeathRecord) -> str:
    return f"{death.datetime}::{death.description}"

async def monitor_deaths():
    html = await fetch_deaths_html()
    current_deaths = parse_deaths(html)

    last_keys = load_last_deaths()
    new_deaths = []

    for death in current_deaths:
        key = generate_death_key(death)
        if key not in last_keys:
            new_deaths.append(death)
            last_keys.add(key)

    if new_deaths:
        for death in reversed(new_deaths):  # Envia do mais antigo para o mais novo
            await send_discord_message(
                f"💀 **{death.datetime}**\n\n{death.description}",
                settings.DISCORD_WEBHOOK_URL_DEATH
            )
        save_last_deaths({generate_death_key(d) for d in current_deaths})