# backend/models/player.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class PlayerSettings:
    """Preferências de interface e jogabilidade."""
    brief_mode: bool = False       
    compact_combat: bool = False   
    color_scheme: str = "default"  
    screen_width: int = 80         
    auto_loot: bool = False        

@dataclass
class Player:
    """
    A Entidade Mestra. 
    """
    # Identificação & Conta
    id: str
    name: str # CORREÇÃO: Renomeado de 'username' para 'name'
    email: str = "" 
    is_admin: bool = False
    
    # Core RPG
    race: str = "humano"
    player_class: str = "aventureiro"
    level: int = 1
    experience: int = 0
    
    # Estado Volátil
    location_vnum: str = "10001" 
    hp: int = 100
    max_hp: int = 100
    mana: int = 50
    max_mana: int = 50
    
    # Inventário e Equipamento
    inventory: List[str] = field(default_factory=list)
    equipment: Dict[str, str] = field(default_factory=dict)
    
    # Configurações & Meta
    settings: PlayerSettings = field(default_factory=PlayerSettings)
    is_dead: bool = False
    
    created_at: datetime = field(default_factory=datetime.now)
    last_login: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_orm(cls, db_player) -> "Player":
        """
        RITUAL DE RESSURREIÇÃO.
        """
        attrs = db_player.attributes or {}
        
        return cls(
            id=str(db_player.id),
            name=db_player.name, # Mapeia direto do DB (que já é 'name')
            
            race=db_player.race,
            player_class=db_player.player_class,
            level=db_player.level,
            experience=db_player.experience,
            
            location_vnum=db_player.current_room_vnum or "10001",
            
            hp=attrs.get("hp", 100),
            max_hp=attrs.get("max_hp", 100),
            mana=attrs.get("mana", 50),
            max_mana=attrs.get("max_mana", 50),
            
            inventory=db_player.inventory or [],
            equipment=db_player.equipment or {},
            
            is_dead=db_player.is_dead,
            created_at=db_player.created_at or datetime.now(),
            last_login=db_player.updated_at or datetime.now()
        )

    def get_stats_dict(self) -> dict:
        return {
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "settings": {
                "brief_mode": self.settings.brief_mode,
                "auto_loot": self.settings.auto_loot
            }
        }

    def __repr__(self):
        return f"<Player '{self.name}' (Lvl {self.level}) @ {self.location_vnum}>"