import os
import json
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from core.config import settings

from core.config import settings
from discord_notifier.notifier import send_discord_message
from apps.online_monitor.models import Player

ONLINE_URL = f"{settings.BASE_URL}/character/online"
CHARACTER_BASE_URL = f"{settings.BASE_URL}/character/view/"
CACHE_FILE = "data/last_online.json"

def load_last_online() -> dict:
    if not os.path.exists(CACHE_FILE):
        # Cria o arquivo com conteúdo vazio se não existir
        with open(CACHE_FILE, "w") as f:
            json.dump({}, f)
        return {}
    with open(CACHE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("[WARN] Erro ao ler JSON. Recriando cache.")
            return {}
    
def save_last_online(data: dict):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[SALVO] Cache de players online atualizado ({len(data)} players).")
    except Exception as e:
        print(f"[ERRO] Falha ao salvar {CACHE_FILE}: {e}")

def format_discord_message(player: Player) -> str:
    hora = datetime.now().strftime("%H:%M:%S")
    if player.guild == "Red Sky":
        return f"[FRIEND-{hora}] Acabou de logar: {player.name} (Level {player.level}) - {player.vocation}"
    elif player.guild == "Carteira Assinada":
        return f"[HUNTED-{hora}] Acabou de logar: {player.name} (Level {player.level}) - {player.vocation}"
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

async def get_player_details(name: str) -> Player | None:
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
            elif "Carteira Assinada" in value:
                guild = "Carteira Assinada"

    if level < 400:
        print(f"[DEBUG] Ignorado {name}: level {level} < 400")
        return None

    return Player(name=name, vocation=vocation, level=level, guild=guild)

async def monitor_online():
    html = await fetch_html(ONLINE_URL)
    current_names = parse_online_players(html)

    if not current_names:
        print("[AVISO] Nenhum jogador online detectado. Ignorando rodada para preservar cache.")
        return

    cache = load_last_online()
    print(f"[INFO] Jogadores online detectados: {len(current_names)}")
    print(f"[INFO] Cache atual: {len(cache)} jogadores notificados")

    for name in current_names:
        if name not in cache:
            try:
                print(f"[DEBUG] Analisando: {name}")
                player = await get_player_details(name)

                if player is None:
                    continue  # Level < 400, ignorado sem cache

                if player.guild in ["Red Sky", "Carteira Assinada"]:
                    msg = format_discord_message(player)
                    if msg:
                        await send_discord_message(msg, settings.DISCORD_WEBHOOK_URL_ONLINE)

                cache[name] = True
                save_last_online(cache)
                print(f"[DEBUG] Cacheando {name} (Level {player.level})")

            except Exception as e:
                print(f"[ERRO] Falha ao obter detalhes de {name}: {e}")



    # Remove jogadores que deslogaram
    names_to_remove = [n for n in cache if n not in current_names]
    for n in names_to_remove:
        del cache[n]

    save_last_online(cache)
    print(f"[DEBUG] Cache persistido com {len(cache)} jogadores:")
    print(json.dumps(cache, indent=2))
