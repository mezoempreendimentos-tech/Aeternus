# backend/main.py
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- CONFIG & UTILS ---
from backend.config.server_config import HOST, PORT, LOG_LEVEL
from backend.utils.logger import logger

# --- MOTORES DO JOGO ---
from backend.game.world.world_manager import WorldManager
from backend.game.engines.time.manager import TimeEngine
from backend.game.engines.ai.nemesis import NemesisEngine
from backend.game.engines.ai.ecosystem import EcosystemEngine
from backend.game.engines.combat.manager import CombatManager
from backend.handlers.command_handler import CommandHandler

# --- MODELOS ---
from backend.models.character import Character

# ============================================================================
# CICLO DE VIDA (LIFESPAN)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    O 'Big Bang' do Universo Aeternus.
    Inicializa todos os sistemas na ordem correta de dependência.
    """
    logger.info("⚡ INICIANDO O SERVIDOR AETERNUS MUD ⚡")
    
    # 1. WORLD MANAGER (O Palco)
    # Carrega VNUMs, Templates e cria as Salas estáticas
    world_manager = WorldManager()
    await world_manager.start_up()
    
    # 2. AI ENGINES (A Vida de Fundo)
    # Nemesis controla evolução individual, Ecosystem controla a cadeia alimentar
    nemesis_engine = NemesisEngine()
    ecosystem_engine = EcosystemEngine(world_manager, nemesis_engine)
    
    # 3. COMBAT ENGINE (O Juiz da Dor)
    # Gerencia turnos, dano e sessões de luta
    combat_manager = CombatManager(world_manager)
    
    # 4. TIME ENGINE (O Relógio)
    # Controla dias, meses, estações e persistência (save/load)
    time_engine = TimeEngine()
    
    # 5. COMMAND HANDLER (A Interação)
    # Traduz texto ("norte", "matar") em funções do jogo
    # Injetamos o combat_manager para permitir o comando 'matar'
    command_handler = CommandHandler(world_manager, combat_manager)
    
    # 6. WIRING (Conexões Neurais)
    # Conecta o 'Heartbeat' do tempo aos motores que precisam rodar periodicamente
    
    # A cada 10s (Tick Global): O Ecossistema roda
    time_engine.register_global_subscriber(ecosystem_engine.run_simulation_cycle)
    
    # A cada 2s (Tick Combate): Resolve os rounds de batalha
    time_engine.register_combat_subscriber(combat_manager.process_round)
    
    # Log periódico do tempo de jogo (debug visual)
    async def log_game_status(date):
        combat_count = len(combat_manager.sessions)
        if combat_count > 0:
            logger.info(f"⏳ Tempo: {date} | Combates: {combat_count} 🔥")
        # else:
            # logger.debug(f"⏳ Tempo: {date}")
            
    time_engine.register_global_subscriber(log_game_status)
    
    # 7. INÍCIO DO LOOP
    # O time_engine carrega o save (gamestate.json) automaticamente aqui
    await time_engine.start_loop()
    
    # 8. EXPORTA PARA O ESTADO DA APP (Para rotas acessarem)
    app.state.world = world_manager
    app.state.time = time_engine
    app.state.combat = combat_manager
    app.state.command_handler = command_handler
    
    # --- CRIAÇÃO DE PERSONAGEM DE TESTE (ADMIN) ---
    if world_manager.rooms:
        # Pega a primeira sala disponível
        start_vnum = list(world_manager.rooms.keys())[0]
        
        # Cria char Admin apenas se não houver persistência de player (futuro)
        admin_char = Character(
            id=1,
            player_id=1,
            name="Criador",
            race_id="human_imperium",
            class_id="iron_vanguard",
            location_vnum=start_vnum
        )
        # Equipamentos de teste (opcional)
        # admin_char.equipment['main_hand'] = "some_uuid"
        
        world_manager.add_player(admin_char)
        logger.info(f"🧙 CHAR DE TESTE CRIADO: 'Criador' (ID 1) na Sala {start_vnum}")
    else:
        logger.warning("⚠️ Nenhuma sala carregada! Verifique data/rooms.json.")

    logger.info("✅ AETERNUS ONLINE. O mundo respira.")
    
    yield # O servidor roda aqui...
    
    # --- SHUTDOWN ---
    logger.info("🛑 DESLIGANDO SERVIDOR...")
    
    # Salva o estado do tempo
    time_engine.save_state()
    logger.info("💾 Tempo salvo.")

# ============================================================================
# APP FASTAPI
# ============================================================================

app = FastAPI(
    title="AETERNUS MUD",
    description="Engine de MUD com Ecossistema Vivo, Combate Tático e Tempo Persistente.",
    version="0.5.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ENDPOINTS
# ============================================================================

class CommandRequest(BaseModel):
    player_id: int
    command: str

@app.post("/api/command")
async def execute_command(req: CommandRequest):
    """
    Endpoint principal de jogo.
    Envia comandos textuais e recebe a resposta processada.
    """
    if not hasattr(app.state, "command_handler"):
        raise HTTPException(status_code=503, detail="Game loading")
        
    handler: CommandHandler = app.state.command_handler
    
    # Processa o comando
    response_text = await handler.process(req.player_id, req.command)
    
    return {"response": response_text}

@app.get("/status")
async def game_status():
    """Painel de Controle."""
    if not hasattr(app.state, "time"):
        return {"status": "loading"}
    
    world: WorldManager = app.state.world
    combat: CombatManager = app.state.combat
    current_date = app.state.time.get_current_date()
    
    return {
        "status": "online",
        "game_time": str(current_date),
        "season": current_date.season_name,
        "metrics": {
            "rooms_loaded": len(world.rooms),
            "players_online": len(world.players),
            "active_npcs": len(world.active_npcs),
            "active_items": len(world.active_items),
            "active_combats": len(combat.sessions),
            "zones_active": len(world.zone_states)
        }
    }

if __name__ == "__main__":
    import uvicorn
    # Roda o servidor
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)