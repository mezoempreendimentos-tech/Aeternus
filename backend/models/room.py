# backend/models/room.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class RoomExit:
    """Define uma saída da sala."""
    target_vnum: int    # VNUM da sala alvo
    direction: str      # north, south, up, down, etc.
    description: str
    is_hidden: bool = False
    is_locked: bool = False
    key_vnum: Optional[int] = None  # VNUM da chave necessária
    required_perception: int = 0

@dataclass
class RoomSensory:
    """A atmosfera sensorial da sala para imersão."""
    visual: str
    auditory: Optional[str] = None
    olfactory: Optional[str] = None
    tactile: Optional[str] = None
    taste: Optional[str] = None

@dataclass
class Room:
    """
    Representação de um espaço no mundo.
    Utiliza VNUM e Flags Ambientais.
    """
    vnum: int
    zone_id: int
    title: str
    
    # Descrições Narrativas
    description_day: str
    description_night: Optional[str] = None
    
    # Camada Sensorial
    sensory: RoomSensory = field(default_factory=lambda: RoomSensory(visual="Nada distinto."))
    
    # Sistema de Flags Ambientais
    # Ex: ["INDOOR", "TAVERN", "DARK", "TOXIC"]
    flags: List[str] = field(default_factory=list)
    
    # Conteúdo (IDs dinâmicos das instâncias presentes)
    exits: Dict[str, RoomExit] = field(default_factory=dict)
    items_here: List[str] = field(default_factory=list)  # Lista de UUIDs de Itens
    npcs_here: List[str] = field(default_factory=list)   # Lista de UUIDs de NPCs
    players_here: List[int] = field(default_factory=list) # Lista de IDs de Players

    def has_flag(self, flag: str) -> bool:
        """Verifica se a sala possui uma característica específica."""
        return flag.upper() in [f.upper() for f in self.flags]

    def get_description(self, time_is_night: bool = False) -> str:
        if time_is_night and self.description_night:
            return self.description_night
        return self.description_day