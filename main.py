import asyncio
import logging
from aeternus.core.connection import Connection
from aeternus.game.world import world
from aeternus.core.config import settings
from aeternus.game.combat.gameloop import gameloop

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger("Core")

async def handle_client(reader, writer):
    conn = Connection(reader, writer)
    await conn.read_loop()

async def main():
    print(f"""
    ╔════════════════════════════════════════╗
      Iniciando {settings.GAME_NAME}
      Porta: {settings.SERVER_PORT}
    ╚════════════════════════════════════════╝
    """)
    
    world.load_assets()
    
    server = await asyncio.start_server(
        handle_client, 
        settings.SERVER_HOST, 
        settings.SERVER_PORT
    )
    
    addr = server.sockets[0].getsockname()
    log.info(f"Portal aberto em {addr}.")

    # Inicia o Loop e guarda a referência da tarefa
    loop_task = asyncio.create_task(gameloop.start())

    try:
        await server.serve_forever()
    except asyncio.CancelledError:
        pass
    finally:
        # Se o servidor parar, cancela o loop
        loop_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.warning("Shutdown manual.")