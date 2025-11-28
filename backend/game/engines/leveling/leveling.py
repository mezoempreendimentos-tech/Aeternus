# backend/game/engines/leveling/leveling.py
import math
import logging

logger = logging.getLogger(__name__)

# --- CONSTANTES DE CALIBRAGEM ---
BASE_XP_REQ = 2000       
GROWTH_RATE = 1.08       # +8.0% por nível (Curva Suave)
REMORT_PENALTY = 0.10    # +10% por Remort

# XP dos Monstros
MOB_BASE_XP = 100        
MOB_GROWTH = 1.058       

class LevelingEngine:
    """
    Motor de Progressão.
    Gerencia curvas de XP, ganhos e level up.
    """
    
    @staticmethod
    def get_xp_required(current_level: int, remort_count: int = 0) -> int:
        """Calcula XP necessário para o PRÓXIMO nível."""
        if current_level < 1: return BASE_XP_REQ
        if current_level >= 100: return 0 
        
        base_req = BASE_XP_REQ * math.pow(GROWTH_RATE, current_level - 1)
        remort_mult = 1.0 + (remort_count * REMORT_PENALTY)
        
        return int(base_req * remort_mult)

    @staticmethod
    def calculate_mob_xp(mob_level: int) -> int:
        """Calcula XP base de um monstro."""
        if mob_level < 1: return 10
        xp = MOB_BASE_XP * math.pow(MOB_GROWTH, mob_level - 1)
        return int(xp)

    @staticmethod
    def calculate_xp_gain(player, source_type: str, amount: int, target_level: int = 1) -> int:
        """Calcula ganho final com multiplicadores de classe."""
        multipliers = {
            "novice":        {"damage": 1.0, "heal": 1.0, "kill": 1000.0, "tank": 1.0},
            "iron_vanguard": {"damage": 0.8, "heal": 0.0, "kill": 1.0,    "tank": 4.0}, 
            "mage":          {"damage": 1.5, "heal": 0.0, "kill": 1.2,    "tank": 0.1},
            "cleric":        {"damage": 0.5, "heal": 4.0, "kill": 0.5,    "tank": 0.5},
            "rogue":         {"damage": 1.5, "heal": 0.0, "kill": 1.0,    "tank": 0.0},
            "warrior":       {"damage": 1.0, "heal": 0.0, "kill": 1.5,    "tank": 1.5}
        }
        
        class_id = getattr(player, "class_id", "warrior")
        class_mults = multipliers.get(class_id, multipliers["warrior"])
        role_mult = class_mults.get(source_type, 1.0)
        
        # Base XP
        if source_type == "kill":
            base_value = LevelingEngine.calculate_mob_xp(target_level)
        else:
            base_value = amount 

        # Penalidade de Nível
        level_diff = target_level - player.level
        level_penalty = 1.0
        
        if level_diff <= -10: level_penalty = 0.0 
        elif level_diff <= -5: level_penalty = 0.2 
        elif level_diff <= -2: level_penalty = 0.8 
        elif level_diff >= 3:  level_penalty = 1.2 
        elif level_diff >= 5:  level_penalty = 1.5 
        
        final_xp = int(base_value * role_mult * level_penalty)
        return max(0, final_xp)

    @staticmethod
    def award_xp(player, amount: int) -> list[str]:
        """Aplica XP e processa Level Up."""
        if amount <= 0: return []
        if player.level >= 100: return [] 

        player.experience += amount
        msgs = []
        
        while True:
            remort = getattr(player, "remort_count", 0)
            req = LevelingEngine.get_xp_required(player.level, remort)
            
            if player.experience >= req:
                player.experience -= req
                player.level += 1
                
                # Bônus de Level Up
                con = player.attributes["constitution"].total if hasattr(player, "attributes") else 10
                inte = player.attributes["intelligence"].total if hasattr(player, "attributes") else 10
                
                player.hp.maximum += 10 + int(con / 2)
                player.hp.current = player.hp.maximum
                
                player.mana.maximum += 5 + int(inte / 2)
                player.mana.current = player.mana.maximum
                
                msgs.append(f"\n✨ LEVEL UP! Nível {player.level} alcançado! ✨")
                if player.level == 100:
                    msgs.append("\n🌟 MESTRIA ALCANÇADA. O ALTAR AGUARDA SEU RENASCIMENTO. 🌟")
            else:
                break
                
        return msgs