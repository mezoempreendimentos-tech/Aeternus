import asyncio
import logging
from typing import Optional

from backend.config.server_config import TELNET_HOST, TELNET_PORT
from backend.db.base import SessionLocal
from backend.db.queries import get_player_by_name, create_player
from backend.models.player import Player
from backend.handlers.command_handler import CommandHandler
from backend.game.world.world_manager import WorldManager

logger = logging.getLogger(__name__)

class TelnetServer:
    def __init__(self, world_manager: WorldManager, command_handler: CommandHandler):
        self.world = world_manager
        self.handler = command_handler
        self.server = None

    async def start(self):
        self.server = await asyncio.start_server(
            self.handle_client, TELNET_HOST, TELNET_PORT
        )
        logger.info(f"🔌 PORTAL TELNET ABERTO EM {TELNET_HOST}:{TELNET_PORT}")
        
        async with self.server:
            await self.server.serve_forever()

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        logger.info(f"Nova conexão Telnet de {addr}")

        async def send(msg: str):
            writer.write(f"{msg}\r\n".encode('utf-8'))
            await writer.drain()

        async def read_input(prompt: str = "") -> str:
            if prompt:
                writer.write(prompt.encode('utf-8'))
                await writer.drain()
            data = await reader.readline()
            if not data: return ""
            return data.decode('utf-8').strip()

        try:
            # --- AUTENTICAÇÃO ---
            await send("\r\n" + "="*40)
            await send("      ⚔️  AETERNUS MUD  ⚔️")
            await send("="*40)
            
            player_id: Optional[str] = None
            db = SessionLocal()

            while not player_id:
                await send("\n1. Entrar (Login)")
                await send("2. Criar Nova Lenda (Registro)")
                await send("3. Sair")
                
                choice = await read_input("\nEscolha: ")
                
                if choice == "1":
                    # LOGIN
                    user = await read_input("Usuario: ")
                    pwd = await read_input("Senha: ") 
                    
                    db_player = get_player_by_name(db, user)
                    
                    # Verificação Simples de Senha
                    if db_player:
                        # Se tiver senha no banco, confere. Se não tiver (contas antigas), deixa passar.
                        if db_player.password_hash and db_player.password_hash != pwd:
                            await send("\n[ERRO] Senha incorreta.")
                            continue
                            
                        player = Player.from_orm(db_player)
                        self.world.add_player(player)
                        player_id = player.id
                        await send(f"\nBem-vindo de volta, {player.name}!")
                    else:
                        await send("\n[ERRO] Alma nao encontrada.")

                elif choice == "2":
                    # REGISTRO
                    user = await read_input("Novo Usuario: ")
                    
                    if get_player_by_name(db, user):
                        await send("\n[ERRO] Nome ja existe.")
                        continue

                    # CORREÇÃO: Agora pedimos a senha
                    pwd = await read_input("Defina sua Senha: ")
                    race = await read_input("Raca (humano/elfo/anao): ")
                    
                    try:
                        # Passamos a senha para a criação
                        db_player = create_player(db, user, race or "humano", "novice", password=pwd)
                        player = Player.from_orm(db_player)
                        self.world.add_player(player)
                        player_id = player.id
                        await send(f"\n[SUCESSO] Bem-vindo, {player.name}.")
                    except Exception as e:
                        await send(f"\n[ERRO] Falha ao criar: {e}")

                elif choice == "3":
                    writer.close()
                    await writer.wait_closed()
                    db.close()
                    return

            db.close()

            # --- GAME LOOP ---
            await send("-" * 40)
            initial_view = await self.handler.process(player_id, "olhar")
            await send(initial_view)
            
            while True:
                command = await read_input("\n> ")
                if not command: continue
                if command.lower() in ["quit", "sair", "exit"]:
                    await send("Desconectando...")
                    break
                
                response = await self.handler.process(player_id, command)
                await send(response)

        except Exception as e:
            logger.error(f"Erro Telnet: {e}")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except: pass