from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import time

class Element(str, Enum):
    FIRE = "fire"
    WATER = "water"
    EARTH = "earth"
    AIR = "air"
    LIGHTNING = "lightning"
    ICE = "ice"
    HOLY = "holy"
    SHADOW = "shadow"
    NATURE = "nature"
    ARCANE = "arcane"
    LIFE = "life"
    DEATH = "death"
    VOID = "void"

class SpellType(str, Enum):
    OFFENSIVE = "offensive"       # Dano direto (Fireball)
    DEFENSIVE = "defensive"       # Buffs/Escudos
    SUMMONING = "summoning"       # Invoca NPCs
    ENCHANTMENT = "enchantment"   # Altera itens
    RITUAL = "ritual"             # Efeito ambiental

class ResearchState(str, Enum):
    """Passos do ritual interativo."""
    WAITING_ELEMENTS = "waiting_elements"
    WAITING_CATALYST = "waiting_catalyst"
    CONFIRMATION = "confirmation"

@dataclass
class MagicComponent:
    vnum: str
    name: str
    description: str
    component_type: str
    rarity: str
    affinities: List[str]
    enhances: Dict[str, Any] = field(default_factory=dict)
    stability_bonus: float = 0.0
    is_consumed: bool = True

@dataclass
class SpellFormula:
    vnum: int
    name: str
    spell_type: SpellType
    tier: int
    primary_element: Element
    mana_cost: int
    base_power: int = 0    
    duration: int = 0
    range: int = 15
    cast_time: float = 2.0
    cooldown: float = 5.0
    
    description: str = ""
    created_by: str = "System"
    volatility_score: float = 0.0 # 0.0 = Seguro, 1.0 = Mortal
    
    # Metadados específicos
    summon_template_vnum: Optional[int] = None
    effects: List[Dict] = field(default_factory=list)

@dataclass
class ResearchSession:
    """O estado mental do jogador enquanto está no laboratório."""
    player_id: int
    state: ResearchState
    start_time: float = field(default_factory=time.time)
    selected_elements: List[str] = field(default_factory=list)
    added_catalysts: List[str] = field(default_factory=list)