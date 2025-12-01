import logging
import json
from typing import Dict
from pathlib import Path

from backend.game.engines.magic.definitions import SpellFormula, SpellType
from backend.game.engines.magic.catalyst_system import CatalystSystem
from backend.models.character import Character

logger = logging.getLogger(__name__)

class MagicManager:
    def __init__(self, world_manager):
        self.world = world_manager
        self.spells: Dict[int, SpellFormula] = {}
        self.catalyst_system = CatalystSystem(self)
        self.data_dir = Path("data")
        self.dynamic_spells_path = self.data_dir / "dynamic_spells.json"

    async def start_up(self):
        self.catalyst_system.load_data()
        # Aqui carregaria magias salvas
        logger.info("🔮 MagicManager: Laboratórios e Linhas de Ley ativos.")

    def register_dynamic_spell(self, spell: SpellFormula):
        self.spells[spell.vnum] = spell
        # Salvar em JSON aqui

    def get_research_session(self, player_id: int):
        return self.catalyst_system.active_sessions.get(player_id)

    async def cast_spell(self, caster: Character, spell_vnum: int, target_str: str = "") -> str:
        spell = self.spells.get(spell_vnum)
        if not spell: return "Magia desconhecida."
        
        # Custo
        if caster.mana.current < spell.mana_cost: return "Mana insuficiente."
        caster.mana.current -= spell.mana_cost

        # Roteamento
        if spell.spell_type == SpellType.OFFENSIVE:
            return await self._cast_offensive(caster, spell, target_str)
        elif spell.spell_type == SpellType.SUMMONING:
            return await self._cast_summon(caster, spell)
        
        return f"Você conjura {spell.name}, mas o efeito é sutil demais (WIP)."

    async def _cast_offensive(self, caster, spell, target_str):
        room = self.world.get_room(caster.location_vnum)
        target = None
        for uid in room.npcs_here:
            npc = self.world.get_npc(uid)
            if npc and target_str.lower() in npc.name.lower():
                target = npc; break
        
        if not target: return "Alvo não encontrado."
        
        dmg = spell.base_power
        target.current_hp -= dmg
        msg = f"🔥 **{caster.name}** lança {spell.name} em {target.name} causando **{dmg}** dano!"
        
        if target.current_hp <= 0:
            msg += " O alvo foi obliterado!"
            self.world.kill_npc(target.uid)
            
        return msg

    async def _cast_summon(self, caster, spell):
        npc = self.world.spawn_npc(100001, caster.location_vnum) # Placeholder ID
        if npc:
            npc.name = f"Servo de {caster.name}"
            return f"🔮 O ar tremula e **{npc.name}** surge para servir!"
        return "A invocação falhou."