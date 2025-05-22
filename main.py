import asyncio
from core.config import settings
from apps.deaths_monitor.service import monitor_deaths
# from app.online_monitor.service import monitor_online

CHECK_INTERVAL = 30

async def main_loop():
    print("Bot de mortes NTO iniciado.")

    while True:
        try:
            await asyncio.gather(
                monitor_deaths(),
                # monitor_online(),
            )
        except Exception as e:
            print(f"[ERRO] Exceção no loop principal: {e}")
            await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:  
        print("Bot de mortes NTO encerrado.")