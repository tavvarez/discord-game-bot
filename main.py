import asyncio
from apps.level_monitor.service import monitor_level_ups
from core.config import settings
from apps.deaths_monitor.service import monitor_deaths
from apps.online_monitor.service import monitor_online

CHECK_INTERVAL = 390

async def main_loop():
    print("Bot monitorando mortes e players online.")

    while True:
        try:
            await asyncio.gather(
                monitor_deaths(),
                # monitor_online(),
                # monitor_level_ups()
            )
            await asyncio.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"[ERRO] Exceção no loop principal: {e}")
            await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:  
        print("Bot de mortes NTO encerrado.")