# backend/models/item.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid

@dataclass
class ItemDamage:
    min_dmg: int
    max_dmg: int
    damage_type: str     
    speed: float = 1.0   

@dataclass
class ItemAttribute:
    attribute_name: str
    value: int

@dataclass
class ItemTemplate:
    """BLUEPRINT (VNUM)."""
    vnum: int            
    name: str            
    description: str     
    
    type: str            
    rarity: str          
    slot: Optional[str]  
    
    # Propriedades Base
    damage: Optional[ItemDamage] = None
    armor_value: int = 0
    weight: float = 0.0
    base_value: int = 0
    durability_max: int = 100
    
    # --- NOVO CAMPO: Verbo de Ataque Personalizado ---
    # Ex: "fatia", "esmaga", "morde", "ferroa"
    attack_verb: Optional[str] = None
    
    flags: List[str] = field(default_factory=list)
    requirements: Dict[str, int] = field(default_factory=dict)
    attributes: List[ItemAttribute] = field(default_factory=list)

    @property
    def is_ancient(self) -> bool:
        return self.vnum <= 99999

@dataclass
class ItemInstance:
    """INSTÂNCIA (UUID)."""
    uid: str = field(default_factory=lambda: str(uuid.uuid4()))
    template_vnum: int = 0  
    durability_current: int = 100
    quality: int = 100      
    owner_character_id: Optional[int] = None
    container_uid: Optional[str] = None 
    room_vnum: Optional[int] = None     
    custom_name: Optional[str] = None

    @property
    def is_broken(self) -> bool:
        return self.durability_current <= 0