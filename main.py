import asyncio
import logging
from aeternus.core.connection import Connection
from aeternus.game.world import world
from aeternus.core.config import settings # <--- A Nova Autoridade

# Configuração de Log (Usando settings)
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger("Core")

async def handle_client(reader, writer):
    """Chamado toda vez que alguém conecta via Telnet."""
    # Passamos o IP para o log
    addr = writer.get_extra_info('peername')
    log.info(f"Nova conexão recebida de: {addr}")
    
    conn = Connection(reader, writer)
    await conn.read_loop()

async def main():
    print(f"""
    ╔════════════════════════════════════════╗
      Iniciando {settings.GAME_NAME}
      Modo Debug: {settings.DEBUG_MODE}
      Porta: {settings.SERVER_PORT}
    ╚════════════════════════════════════════╝
    """)
    
    # --- O RITUAL DE CARREGAMENTO ---
    # Agora o world usa os caminhos do config
    world.load_assets()
    
    server = await asyncio.start_server(
        handle_client, 
        settings.SERVER_HOST, 
        settings.SERVER_PORT
    )
    
    addr = server.sockets[0].getsockname()
    log.info(f"Portal aberto em {addr}. Aguardando heróis...")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.warning("Shutdown manual iniciado pelo Arquiteto.")