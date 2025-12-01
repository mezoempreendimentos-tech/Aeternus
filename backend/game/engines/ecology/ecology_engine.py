# backend/game/engines/ecology/ecology_engine.py
"""
MOTOR ECOLÓGICO COMPLETO
Integra ResourceManager, Ciclos de Tempo e IA.
"""
import asyncio
import logging
import random
from typing import Optional
from backend.game.engines.ecology.resource_management import ResourceManager

logger = logging.getLogger(__name__)

class EcologyEngine:
    def __init__(self, world_manager, time_engine, grimoire_engine, ollama_service=None):
        self.world = world_manager
        self.time = time_engine
        self.grimoire = grimoire_engine
        self.ollama = ollama_service
        
        # Subsistema de Recursos
        self.resource_manager = ResourceManager(world_manager, time_engine)
        
        self.enabled = True
        self.ecology_tick_count = 0

    async def run_ecology_tick(self, game_date):
        """O coração pulsante da natureza. Executado periodicamente pelo TimeEngine."""
        if not self.enabled:
            return
        
        self.ecology_tick_count += 1
        
        # 1. Ciclo de Respawn de Recursos (A cada 6 ticks ecológicos)
        if self.ecology_tick_count % 6 == 0:
            # Por enquanto, assumimos Zona 1 (Floresta) como principal
            await self.resource_manager.run_respawn_cycle(zone_id=1)

        # 2. IA de Comportamento (Ollama) - Processamento em Lote Opcional
        # (Implementação simplificada para não sobrecarregar o loop)
        if self.ollama and self.ecology_tick_count % 10 == 0:
            # Aqui poderíamos chamar uma função assíncrona para gerar "flavor text" 
            # de animais caçando, mas deixaremos passivo por enquanto.
            pass

    def get_zone_report(self, zone_id: int) -> str:
        """Gera um relatório completo para o comando 'fauna'."""
        date = self.time.get_current_date()
        
        # Dados do Clima (Simulado base)
        weather_desc = "Céu limpo"
        if date.season_name == "Inverno": weather_desc = "Frio cortante e neve leve"
        elif date.season_name == "Verão": weather_desc = "Calor úmido e sol forte"
        
        # Dados de Recursos
        resources_report = self.resource_manager.get_resource_report(zone_id)
        
        # Contagem Geral
        total_npcs = 0
        active_predators = 0
        if self.world.rooms:
            for room in self.world.rooms.values():
                if room.zone_id == zone_id:
                    total_npcs += len(room.npcs)
                    for npc in room.npcs:
                        if npc.has_flag("AGGRESSIVE") or npc.has_flag("PREDATOR"):
                            active_predators += 1

        buffer = [
            "📜 RELATÓRIO ECOLÓGICO E CLIMÁTICO",
            f"📅 Data: {date}",
            f"🍂 Estação: {date.season_name} | 🌤️ Clima: {weather_desc}",
            "-" * 40,
            f"🐾 Vida na Zona {zone_id}: {total_npcs} entidades detectadas.",
            f"🐺 Predadores Ativos: {active_predators}",
            "-" * 40,
            resources_report,
            "-" * 40
        ]
        
        # Toque de Lore/IA se disponível
        if self.grimoire:
            # Verifica se há alguma lenda local sobre bestas
            pass 

        return "\n".join(buffer)

    def get_species_status(self, species_name_query: str) -> str:
        """Rastreia uma espécie específica."""
        count = 0
        found_in_rooms = []
        
        query = species_name_query.lower()
        
        for room in self.world.rooms.values():
            for npc in room.npcs:
                if query in npc.name.lower():
                    count += 1
                    if len(found_in_rooms) < 3: # Lista apenas as 3 primeiras salas
                        found_in_rooms.append(f"[{room.vnum}] {room.name}")
        
        if count == 0:
            return f"Os rastros de '{species_name_query}' desapareceram ou nunca existiram aqui."
        
        locs = ", ".join(found_in_rooms)
        if count > 3: locs += "..."
        
        return f"👣 RASTREAMENTO: {count} espécimes de '{species_name_query}' encontrados.\n📍 Avistamentos recentes: {locs}"