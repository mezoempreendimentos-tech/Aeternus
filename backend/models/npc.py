# backend/models/npc.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid

# --- ESTRUTURAS DE BLUEPRINT ---

@dataclass
class NaturalAttack:
    """Define um modo de ataque inato (Garras, Mordida)."""
    name: str           # ex: "Garras Sujas"
    damage_type: str    # ex: "slash"
    verb: str           # ex: "arranha"
    damage_mult: float = 1.0 # Multiplicador sobre o dano base do nível

@dataclass
class BodyPartTemplate:
    id: str          
    name: str        
    hit_weight: int  
    hp_factor: float 
    flags: List[str] = field(default_factory=list)

@dataclass
class NPCTemplate:
    vnum: int            
    name: str            
    description: str
    
    level: int
    base_hp: int
    body_type: str       
    
    sensory_visual: str
    flags: List[str] = field(default_factory=list)
    loot_table: Dict[int, float] = field(default_factory=dict)
    sensory_auditory: Optional[str] = None
    
    # --- NOVO CAMPO: Lista de Ataques Naturais ---
    natural_attacks: List[NaturalAttack] = field(default_factory=list)

    @property
    def is_ancient(self) -> bool:
        return self.vnum <= 99999

# --- ESTRUTURAS DE INSTÂNCIA (Permanece igual, só copiei para manter o arquivo completo) ---

@dataclass
class BodyPartInstance:
    definition_id: str 
    name: str = "Parte" 
    hp_current: int = 0
    hp_max: int = 0
    flags: List[str] = field(default_factory=list) 
    is_severed: bool = False
    is_broken: bool = False
    def has_flag(self, flag: str) -> bool: return flag.upper() in [f.upper() for f in self.flags]

@dataclass
class NPCKillRecord:
    player_name: str
    player_level: int
    timestamp: float
    method: str

@dataclass
class NPCProgression:
    kills_count: int = 0
    evolution_stage: int = 0
    original_name: str = ""
    dynamic_titles: List[str] = field(default_factory=list)

@dataclass
class NPCInstance:
    uid: str = field(default_factory=lambda: str(uuid.uuid4()))
    template_vnum: int = 0
    name: str = "" 
    level: int = 1 
    current_hp: int = 0
    total_hp: int = 0
    anatomy_state: Dict[str, BodyPartInstance] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)
    progression: NPCProgression = field(default_factory=NPCProgression)
    kill_history: List[NPCKillRecord] = field(default_factory=list)
    room_vnum: int = 0
    aggro_list: Dict[int, int] = field(default_factory=dict)

    @property
    def full_name(self) -> str:
        if self.progression.kills_count > 0 and self.progression.dynamic_titles:
            titles = ", ".join(self.progression.dynamic_titles)
            return f"{self.name}, {titles}"
        return self.name

    def has_flag(self, flag: str) -> bool: return flag.upper() in [f.upper() for f in self.flags]

    def is_alive(self) -> bool:
        if self.current_hp <= 0: return False
        for part in self.anatomy_state.values():
            if part.has_flag("VITAL") and (part.hp_current <= 0 or part.is_severed): return False
        return True