# Constantes Globais

from enum import Enum

class CharacterClass(str, Enum):
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    PRIEST = "priest"

class Race(str, Enum):
    HUMAN = "human"
    ELF = "elf"
    DWARF = "dwarf"
    HALFLING = "halfling"

class ItemType(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    QUEST = "quest"
    CRAFTING = "crafting"

class CombatState(str, Enum):
    IDLE = "idle"
    FIGHTING = "fighting"
    FLEEING = "fleeing"
    DEAD = "dead"

class NPCState(str, Enum):
    IDLE = "idle"
    PATROLLING = "patrolling"
    AGGRO = "aggro"
    TALKING = "talking"
    DEAD = "dead"

# Atributos
ATTRIBUTES = ["strength", "dexterity", "intelligence", "wisdom", "constitution"]

# Efeitos de Combate
COMBAT_EFFECTS = {
    "bleed": {"damage": 5, "duration": 5, "tick_rate": 1},
    "stun": {"miss_chance": 1.0, "duration": 1},
    "haste": {"speed_bonus": 0.2, "duration": 10},
    "slow": {"speed_penalty": 0.5, "duration": 8},
    "burn": {"damage": 3, "duration": 6, "tick_rate": 1},
}
