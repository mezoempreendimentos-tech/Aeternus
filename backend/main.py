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

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(">>> INICIANDO AETERNUS MUD (v0.9 - Grimório & Lendas) <<<")
    
    # 1. Instancia Motores
    world_manager = WorldManager()
    time_engine = TimeEngine()
    
    # WIRING: Conecta o Mundo ao Tempo (Crucial para propagação de lendas)
    # Isso permite que o TimeEngine chame world.grimoire.spread_legend_naturally()
    time_engine.set_world_manager(world_manager)
    
    combat_manager = CombatManager(world_manager)
    command_handler = CommandHandler(world_manager, combat_manager)
    
    # 2. Carrega Dados
    await world_manager.start_up()
    
    # 3. Loops
    time_engine.register_combat_subscriber(combat_manager.process_round)
    await time_engine.start_loop()
    
    # 4. State Injection
    app.state.world = world_manager
    app.state.combat = combat_manager
    app.state.time = time_engine
    app.state.command_handler = command_handler
    
    # 5. Telnet
    telnet_server = TelnetServer(world_manager, command_handler)
    asyncio.create_task(telnet_server.start())
    
    # 6. Auto-Save Players
    async def auto_save_players():
        while True:
            await asyncio.sleep(60)
            db = next(get_db())
            try:
                for pid, char in world_manager.players.items():
                    inv_data = []
                    for item_uid in char.inventory:
                        item = world_manager.get_item(item_uid)
                        if item: inv_data.append(item.__dict__)
                    
                    save_player_state(
                        db, pid, char.location_vnum, 
                        char.get_stats_dict(), char.level, char.experience,
                        inv_data
                    )
            except Exception as e:
                logger.error(f"Erro auto-save: {e}")
            finally:
                db.close()
                
    asyncio.create_task(auto_save_players())
    
    logger.info("[OK] AETERNUS ONLINE.")
    
    # --- O SERVIDOR RODA AQUI ---
    yield
    # --- DESLIGAMENTO ---
    
    # NOVO: Salva grimório antes de desligar
    logger.info("[STOP] Salvando Grimório...")
    if hasattr(world_manager, 'grimoire') and world_manager.grimoire:
        try:
            # Nota: Certifique-se que implementou save_grimoire() no GrimoireEngine
            world_manager.grimoire.save_grimoire()
        except AttributeError:
            logger.warning("GrimoireEngine: Método save_grimoire não encontrado (ainda não implementado?).")
        except Exception as e:
            logger.error(f"Erro ao salvar Grimório: {e}")
    
    logger.info("[STOP] DESLIGANDO...")
    time_engine.save_state()

app = FastAPI(title="AETERNUS MUD", version="0.9.0", lifespan=lifespan)
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
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)