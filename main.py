import asyncio
import logging
from aeternus.core.connection import Connection
from aeternus.game.world import world  # <--- Importamos o Atlas

# Configuração de Log
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger("Aeternus")

async def handle_client(reader, writer):
    """Chamado toda vez que alguém conecta via Telnet."""
    conn = Connection(reader, writer)
    await conn.read_loop()

async def main():
    HOST = '0.0.0.0'
    PORT = 4000

    print(r"""
    Initializing AETERNUS CORE SYSTEM...
    """)
    
    # --- O RITUAL DE CARREGAMENTO ---
    world.load_assets()
    # -------------------------------
    
    server = await asyncio.start_server(handle_client, HOST, PORT)
    
    addr = server.sockets[0].getsockname()
    print(f"\n🔥 O PORTAL ESTÁ ABERTO EM {addr} (Porta {PORT})")
    print("   Use um cliente MUD (Mudlet/PuTTY) para conectar em 'localhost' porta 4000.")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 O servidor foi desligado pelos deuses.")