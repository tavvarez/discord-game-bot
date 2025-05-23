import asyncio
from apps.level_monitor.service import monitor_level_ups

LEVEL_INTERVAL = 360  # segundos

async def loop_monitor_level_ups():
    print("Bot monitorando level ups.")
    while True:
        try:
            await monitor_level_ups()
        except Exception as e:
            print(f"[ERRO] monitor_level_ups: {e}")
        print(f"[LOG] Aguardando {LEVEL_INTERVAL} segundos para o próximo ciclo.")
        await asyncio.sleep(LEVEL_INTERVAL)
        print(f"[LOG] Retomando o ciclo.")

if __name__ == "__main__":
    try:
        asyncio.run(loop_monitor_level_ups())
    except KeyboardInterrupt:
        print("Monitor de level encerrado.")
