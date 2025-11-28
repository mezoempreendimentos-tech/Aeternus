# backend/game/engines/ai/ecosystem.py
import random
import logging
from typing import List, Optional
from backend.models.npc import NPCInstance
from backend.models.room import Room
from backend.game.engines.ai.nemesis import NemesisEngine
from backend.game.utils.vnum import VNum

logger = logging.getLogger(__name__)

class EcosystemEngine:
    """
    O motor que simula a vida selvagem.
    """
    def __init__(self, world_manager, nemesis_engine: NemesisEngine):
        self.world = world_manager
        self.nemesis = nemesis_engine

    async def run_simulation_cycle(self, game_date=None):
        """Executado periodicamente pelo servidor (TimeEngine)."""
        # Itera sobre todas as salas ativas no mundo
        for room in self.world.rooms.values():
            # Pega o estado da zona desta sala
            zone_id, _ = VNum.parse(room.vnum)
            zone_alpha = self.world.get_zone_alpha(zone_id)
            
            await self._process_room_ecology(room, zone_alpha)

    async def _process_room_ecology(self, room: Room, zone_alpha: Optional[NPCInstance]):
        """
        Simula a violência dentro de uma sala.
        """
        # Converte lista de UUIDs para Objetos NPC reais
        npcs_in_room = []
        for uid in room.npcs_here:
            npc_obj = self.world.get_npc(uid)
            if npc_obj:
                npcs_in_room.append(npc_obj)
        
        if len(npcs_in_room) < 2:
            # Lógica de migração poderia entrar aqui (mover NPC para sala vizinha)
            return

        # Separa predadores e presas
        predators = [n for n in npcs_in_room if n.has_flag("PREDATOR") or n.has_flag("AGGRESSIVE")]
        potential_victims = [n for n in npcs_in_room if n not in predators]

        for predator in predators:
            # O Alpha não tolera concorrência do mesmo tipo
            if zone_alpha and predator.uid != zone_alpha.uid and predator.name == zone_alpha.name: # Simplificação por nome/tipo
                 await self._resolve_background_combat(zone_alpha, predator, room)
                 continue

            # Predador caça presa
            if potential_victims:
                victim = random.choice(potential_victims)
                await self._resolve_background_combat(predator, victim, room)
                
            # Canibalismo (Se não há comida)
            elif len(predators) > 1:
                rival = random.choice([p for p in predators if p != predator])
                await self._resolve_background_combat(predator, rival, room)

    async def _resolve_background_combat(self, attacker: NPCInstance, defender: NPCInstance, room: Room):
        """
        Resolve combate rápido (simulado).
        """
        # Power Rating simplificado
        attacker_power = attacker.total_hp * random.uniform(0.8, 1.2)
        defender_power = defender.total_hp * random.uniform(0.8, 1.2)

        if attacker_power > defender_power:
            winner = attacker
            loser = defender
        else:
            winner = defender
            loser = attacker

        # O perdedor morre
        # logger.debug(f"ECOSYSTEM: {winner.name} matou {loser.name} na sala {room.vnum}")
        self.world.kill_npc(loser.uid)
        
        # O vencedor come e pode evoluir
        await self._process_victory(winner, loser, room)

    async def _process_victory(self, winner: NPCInstance, loser: NPCInstance, room: Room):
        # 1. Recupera vida
        heal = int(loser.total_hp * 0.5)
        winner.current_hp = min(winner.total_hp, winner.current_hp + heal)
        
        # 2. Registra kill (Nemesis)
        winner.progression.kills_count += 1
        
        # 3. Evolução
        if self.nemesis._check_evolution_threshold(winner):
            self.nemesis._evolve_npc(winner)

        # 4. Checagem de Alpha da Zona
        if winner.progression.kills_count > 10 and not winner.has_flag("ZONE_ALPHA"):
            self._crowning_moment(winner, room)

    def _crowning_moment(self, npc: NPCInstance, room: Room):
        zone_id, _ = VNum.parse(room.vnum)
        
        # Define no WorldManager quem é o novo alpha
        self.world.set_zone_alpha(zone_id, npc)
        
        npc.flags.append("ZONE_ALPHA")
        npc.progression.dynamic_titles.append("o Apex da Região")
        logger.info(f"👑 NOVO ALPHA: {npc.full_name} assumiu a Zona {zone_id}!")