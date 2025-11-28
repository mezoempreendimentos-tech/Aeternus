# backend/game/engines/combat/formulas.py
import random
import logging
from typing import Tuple, Dict, Any, Optional

from backend.models.character import Character
from backend.models.npc import NPCInstance, BodyPartInstance
from backend.models.item import ItemInstance, ItemTemplate

logger = logging.getLogger(__name__)

class CombatFormulas:
    """
    A Matemática da Dor.
    """

    @staticmethod
    def calculate_hit_chance(attacker, defender, weapon: Optional[ItemTemplate] = None) -> float:
        # --- ATACANTE ---
        atk_dex = CombatFormulas._get_attr(attacker, "dexterity")
        atk_luck = CombatFormulas._get_attr(attacker, "luck")
        atk_perc = CombatFormulas._get_attr(attacker, "perception")
        
        weapon_bonus = 0 
        accuracy = (atk_dex * 2) + atk_perc + (atk_luck * 0.5) + weapon_bonus

        # --- DEFENSOR ---
        def_dex = CombatFormulas._get_attr(defender, "dexterity")
        def_perc = CombatFormulas._get_attr(defender, "perception")
        def_luck = CombatFormulas._get_attr(defender, "luck")
        
        armor_penalty = 0
        evasion = (def_dex * 1.5) + (def_perc * 1.0) + (def_luck * 0.5) - armor_penalty

        # --- O DUELO ---
        base_chance = 60.0
        diff = accuracy - evasion
        
        # Limites (5% a 95%)
        return max(5.0, min(95.0, base_chance + diff)) / 100.0

    @staticmethod
    def select_body_part(defender) -> Tuple[str, Optional[BodyPartInstance]]:
        anatomy = defender.anatomy_state if isinstance(defender, NPCInstance) else defender.anatomy
        if not anatomy: return "body", None

        choices = []
        weights = []
        for part_id, part in anatomy.items():
            if part.is_severed: continue
            choices.append(part_id)
            # Fallback seguro para hit_weight
            weights.append(getattr(part, 'hit_weight', 10))

        if not choices: return "torso", None
        
        selected_id = random.choices(choices, weights=weights, k=1)[0]
        return selected_id, anatomy[selected_id]

    @staticmethod
    def calculate_damage(attacker, weapon_tmpl: Optional[ItemTemplate], is_crit: bool) -> Dict[str, Any]:
        """
        Calcula o dano base.
        Crítico (5% chance): Dano x1.5
        (Fatality é aplicado externamente como Instant Kill)
        """
        str_stat = CombatFormulas._get_attr(attacker, "strength")
        
        # Dano Base
        if weapon_tmpl and weapon_tmpl.damage:
            dmg_min = weapon_tmpl.damage.min_dmg
            dmg_max = weapon_tmpl.damage.max_dmg
            dmg_type = weapon_tmpl.damage.damage_type
        else:
            # Desarmado
            dmg_min = 1
            dmg_max = 3 + int(str_stat / 4)
            dmg_type = "blunt"

        base_dmg = random.randint(dmg_min, dmg_max)
        attribute_bonus = str_stat * 0.5 
        
        total_damage = base_dmg + attribute_bonus
        
        # Se for crítico, aplica multiplicador de 1.5x
        if is_crit:
            total_damage *= 1.5

        return {
            "amount": int(total_damage),
            "type": dmg_type,
            "is_crit": is_crit
        }

    @staticmethod
    def calculate_mitigation(defender, damage_info: Dict, hit_location: Optional[BodyPartInstance]) -> int:
        raw_amount = damage_info["amount"]
        dmg_type = damage_info["type"]
        
        natural_armor = 0
        if hit_location:
            if hit_location.has_flag("ARMORED"): natural_armor += 5
            elif hit_location.has_flag("MAT_STONE"): natural_armor += 10
        
        multiplier = 1.0
        if hit_location:
            # Resistências
            if hit_location.has_flag("MAT_BONE") and dmg_type == "pierce": multiplier = 0.5
            if hit_location.has_flag("MAT_STONE") and dmg_type == "slash": multiplier = 0.3
            # Fraquezas
            if hit_location.has_flag("MAT_BONE") and dmg_type == "blunt": multiplier = 1.5
            if hit_location.has_flag("MAT_WOOD") and dmg_type == "slash": multiplier = 1.2

        final_damage = max(1, (raw_amount * multiplier) - natural_armor)
        return int(final_damage)

    @staticmethod
    def check_severing(damage: int, part: Optional[BodyPartInstance], weapon_flags: list) -> bool:
        if not part or not part.has_flag("SEVERABLE"): return False
        can_cut = "SHARP" in weapon_flags or "SEVERING" in weapon_flags
        if not can_cut: return False
        
        is_massive_hit = damage >= (part.hp_max * 0.5)
        is_fatal_to_part = part.hp_current <= 0
        return is_massive_hit and is_fatal_to_part

    @staticmethod
    def _get_attr(entity, attr_name: str) -> int:
        if hasattr(entity, "attributes") and attr_name in entity.attributes:
            return entity.attributes[attr_name].total
        
        if hasattr(entity, "level"):
            base = 8 + (entity.level * 2)
            if attr_name == "strength" and entity.has_flag("STRONG"): base += 5
            if attr_name == "dexterity" and entity.has_flag("FAST"): base += 5
            return base
        return 10