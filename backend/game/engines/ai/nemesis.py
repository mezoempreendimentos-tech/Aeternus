# backend/game/engines/ai/nemesis.py
import random
import logging
from datetime import datetime
from backend.models.npc import NPCInstance
from backend.models.character import Character

logger = logging.getLogger(__name__)

class NemesisEngine:
    """
    Gerencia a ascensão de NPCs, o sistema de Caça/Caçador e a hierarquia da Zona.
    """
    
    # Títulos dinâmicos baseados no tipo de morte causada
    TITLES_BY_DAMAGE_TYPE = {
        "slash": ["o Cortador", "o Açougueiro", "Lâmina Rubra"],
        "blunt": ["o Quebra-Ossos", "o Esmagador", "Martelo de Carne"],
        "pierce": ["o Perfurador", "o Espeto", "Olho de Agulha"],
        "magic": ["o Arcano", "o Devorador de Almas", "Chama Negra"],
        "poison": ["o Peçonhento", "Língua Podre", "o Tocado pela Peste"]
    }

    async def register_player_death(self, killer_npc: NPCInstance, victim: Character, damage_type: str, zone_state: dict):
        """
        Chamado quando um NPC mata um jogador.
        """
        # 1. Registro
        killer_npc.kill_history.append({
            "player_name": victim.name,
            "level": victim.level,
            "timestamp": datetime.utcnow().timestamp(),
            "method": damage_type
        })
        
        killer_npc.progression.kills_count += 1
        logger.info(f"NEMESIS: {killer_npc.name} matou {victim.name}. Kills totais: {killer_npc.progression.kills_count}")
        
        # 2. Gera Título (Se ainda não tiver muitos)
        if len(killer_npc.progression.dynamic_titles) < 3:
            new_title = self._generate_title(damage_type, victim.name)
            if new_title not in killer_npc.progression.dynamic_titles:
                killer_npc.progression.dynamic_titles.append(new_title)
                
        # 3. Evolução
        if self._check_evolution_threshold(killer_npc):
            self._evolve_npc(killer_npc)
            
        # 4. Disputa de Alpha da Zona (Simplificado)
        # A lógica real de setar alpha deve ser chamada pelo Ecosystem ou WorldManager
        # Aqui apenas marcamos que ele é candidato
        if killer_npc.progression.kills_count >= 5:
            # Lógica futura: disparar evento de disputa
            pass

    def _generate_title(self, damage_type: str, victim_name: str) -> str:
        """Gera um título ofensivo ou grandioso."""
        if random.random() < 0.10:
            return f"o Pesadelo de {victim_name}"
        
        options = self.TITLES_BY_DAMAGE_TYPE.get(damage_type, ["o Assassino"])
        return random.choice(options)

    def _check_evolution_threshold(self, npc: NPCInstance) -> bool:
        """Define se o NPC está pronto para crescer."""
        kills = npc.progression.kills_count
        thresholds = [1, 5, 10, 25, 50]
        return kills in thresholds

    def _evolve_npc(self, npc: NPCInstance) -> str:
        """
        Transforma o NPC.
        Aumenta stats, recupera HP, muda flags.
        """
        npc.progression.evolution_stage += 1
        
        # Buff nos atributos (Curando e aumentando MAX HP)
        old_hp = npc.total_hp
        npc.total_hp = int(npc.total_hp * 1.2) # +20% HP
        npc.current_hp = npc.total_hp          # Cura total
        
        # Adiciona flag de perigo se virar Elite
        if npc.progression.evolution_stage >= 2 and "ELITE" not in npc.flags:
            npc.flags.append("ELITE")
            
        msg = f"EVOLUÇÃO: {npc.name} evoluiu para Estágio {npc.progression.evolution_stage}! (HP: {old_hp} -> {npc.total_hp})"
        logger.info(msg)
        return msg