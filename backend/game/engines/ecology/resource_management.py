# backend/game/engines/ecology/resource_management.py
"""
SISTEMA DE GESTÃO DE RECURSOS ECOLÓGICOS
Gerencia espécies-recurso (presas) com proteção contra extinção.
"""
import logging
import random
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ResourceSpecies:
    species_id: str
    name: str
    template_vnum: int
    minimum_population: int
    optimal_population: int
    maximum_population: int
    respawn_enabled: bool = True
    # Intervalo simples para controle interno (em ticks do ciclo)
    respawn_tick_counter: int = 0
    respawn_threshold: int = 6  # Ticks necessários para tentar respawn

@dataclass
class ZoneResourceState:
    zone_id: int
    total_hunted_today: int = 0
    extinction_events: int = 0
    last_respawn_check: str = ""

class ResourceManager:
    def __init__(self, world_manager, time_engine):
        self.world = world_manager
        self.time = time_engine
        self.resource_species: Dict[str, ResourceSpecies] = {}
        self.zone_states: Dict[int, ZoneResourceState] = {}
        self._load_default_resources()

    def _load_default_resources(self):
        # Configuração Definitiva dos Recursos Básicos
        self.resource_species["rabbit"] = ResourceSpecies(
            species_id="rabbit",
            name="Coelho Selvagem",
            template_vnum=100010,
            minimum_population=5,
            optimal_population=15,
            maximum_population=30
        )
        self.resource_species["rat"] = ResourceSpecies(
            species_id="rat",
            name="Rato Gigante",
            template_vnum=100001,
            minimum_population=8,
            optimal_population=20,
            maximum_population=40
        )
        self.resource_species["deer"] = ResourceSpecies(
            species_id="deer",
            name="Cervo",
            template_vnum=100003,
            minimum_population=2,
            optimal_population=8,
            maximum_population=12
        )

    def _get_zone_state(self, zone_id: int) -> ZoneResourceState:
        if zone_id not in self.zone_states:
            self.zone_states[zone_id] = ZoneResourceState(zone_id=zone_id)
        return self.zone_states[zone_id]

    def _count_population(self, zone_id: int, template_vnum: int) -> int:
        count = 0
        if not self.world.rooms:
            return 0
        
        # Otimização: Iterar apenas salas da zona se possível, mas aqui varremos tudo por segurança
        for room in self.world.rooms.values():
            if room.zone_id == zone_id:
                for npc in room.npcs:
                    if npc.vnum == template_vnum:
                        count += 1
        return count

    async def run_respawn_cycle(self, zone_id: int):
        """Tenta repopular espécies que estão abaixo do ideal."""
        if not self.world.rooms:
            return

        state = self._get_zone_state(zone_id)
        current_date = self.time.get_current_date()
        state.last_respawn_check = str(current_date)
        
        # Filtra salas da zona para spawn
        zone_rooms = [r.vnum for r in self.world.rooms.values() if r.zone_id == zone_id]
        if not zone_rooms:
            return

        for res in self.resource_species.values():
            if not res.respawn_enabled:
                continue
                
            current_pop = self._count_population(zone_id, res.template_vnum)
            
            # Lógica de Spawn: Se estiver abaixo do ideal
            if current_pop < res.optimal_population:
                deficit = res.optimal_population - current_pop
                # Spawna uma fração do déficit para não lotar de uma vez
                to_spawn = max(1, deficit // 2)
                
                spawned_now = 0
                for _ in range(to_spawn):
                    room_vnum = random.choice(zone_rooms)
                    npc = self.world.spawn_npc(res.template_vnum, room_vnum)
                    if npc:
                        spawned_now += 1
                
                if spawned_now > 0:
                    logger.info(f"🌿 RESPAWN [{res.name}]: +{spawned_now} na Zona {zone_id} ({current_pop} -> {current_pop + spawned_now})")

    def get_resource_report(self, zone_id: int) -> str:
        lines = [f"=== RECURSOS NATURAIS (ZONA {zone_id}) ==="]
        for res in self.resource_species.values():
            count = self._count_population(zone_id, res.template_vnum)
            status = "🟢" if count >= res.optimal_population else "🟡" if count >= res.minimum_population else "🔴 CRÍTICO"
            lines.append(f"{status} {res.name}: {count}/{res.optimal_population} (Mín: {res.minimum_population})")
        return "\n".join(lines)