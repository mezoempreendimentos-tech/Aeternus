# backend/main.py
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.config.server_config import HOST, PORT
from backend.utils.logger import logger
from backend.db.base import get_db
from backend.db.queries import get_player_by_id, save_player_state
from backend.game.world.world_manager import WorldManager
from backend.game.engines.time.manager import TimeEngine
from backend.game.engines.combat.manager import CombatManager
from backend.handlers.command_handler import CommandHandler
from backend.models.player import Player 
from backend.models.item import ItemInstance
from backend.api.telnet import TelnetServer
from backend.api.routes import router as api_router

# [NOVO] Importações de IA e Ecologia
from backend.ai.ollama_service import OllamaService
from backend.game.engines.ecology.ecology_engine import EcologyEngine

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(">>> INICIANDO AETERNUS MUD (v1.0 - Grimório & Ecologia Viva) <<<")
    
    # 1. Instancia Motores Básicos
    world_manager = WorldManager()
    time_engine = TimeEngine()
    
    # 2. IA Service (Ollama) - Tentativa de conexão
    try:
        ollama_service = OllamaService()
        logger.info("🧠 IA Neural (Ollama): ONLINE")
    except Exception as e:
        logger.warning(f"🧠 IA Neural (Ollama): OFFLINE ({e}) - Usando fallback lógico.")
        ollama_service = None

    # 3. WIRING: Conecta o Mundo ao Tempo
    time_engine.set_world_manager(world_manager)
    
    # 4. [NOVO] Instancia Motor Ecológico e Injeta no Mundo
    # O Grimoire reside dentro do world_manager nas versões recentes, passamos ele se existir
    grimoire_ref = getattr(world_manager, 'grimoire', None)
    
    ecology_engine = EcologyEngine(
        world_manager=world_manager,
        time_engine=time_engine,
        grimoire_engine=grimoire_ref,
        ollama_service=ollama_service
    )
    # Torna a ecologia acessível globalmente via world_manager
    world_manager.ecology = ecology_engine
    
    # Registra o "Tick Ecológico" no relógio do tempo
    time_engine.register_global_subscriber(ecology_engine.run_ecology_tick)
    logger.info("🌿 Ecossistema: SINCRONIZADO")

    # 5. Motores de Jogo
    combat_manager = CombatManager(world_manager)
    command_handler = CommandHandler(world_manager, combat_manager)
    
    # 6. Salva referências no estado da App
    app.state.world = world_manager
    app.state.time = time_engine
    app.state.combat = combat_manager
    app.state.command_handler = command_handler
    app.state.ecology = ecology_engine # Opcional, para acesso via API se precisar
    
    # 7. Inicialização do Mundo (Carrega JSONs)
    await world_manager.start_up()
    
    # 8. Loop de Tempo
    asyncio.create_task(time_engine.start_loop())
    
    # 9. Servidor Telnet
    telnet_server = TelnetServer(host="0.0.0.0", port=4000, command_handler=command_handler)
    asyncio.create_task(telnet_server.start())
    logger.info("🚪 PORTAL TELNET ABERTO na porta 4000")
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 DESLIGANDO AETERNUS...")
    # Aqui poderia ter time_engine.stop() ou similar

app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(api_router, prefix="/api")

class CommandRequest(BaseModel):
    player_id: str  
    command: str

@app.post("/api/command")
async def execute_command(req: CommandRequest, db: Session = Depends(get_db)):
    handler = app.state.command_handler
    world = app.state.world
    
    player = world.get_player(req.player_id)
    
    if not player:
        db_player = get_player_by_id(db, req.player_id)
        if db_player:
            player_instance = Player.from_orm(db_player)
            
            real_inventory_uids = []
            if db_player.inventory:
                for item_dict in db_player.inventory:
                    try:
                        item = ItemInstance(**item_dict)
                        world.active_items[item.uid] = item
                        real_inventory_uids.append(item.uid)
                    except Exception as e:
                        logger.error(f"Falha ao hidratar item: {e}")
            
            player_instance.inventory = real_inventory_uids
            world.add_player(player_instance)
        else:
            raise HTTPException(status_code=404, detail="Personagem nao encontrado.")

    response_text = await handler.process(req.player_id, req.command)
    return {"response": response_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)