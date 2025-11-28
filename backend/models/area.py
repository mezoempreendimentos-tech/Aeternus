# backend/models/area.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime

@dataclass
class AreaEcology:
    """
    O estado vivo de uma região (Zona).
    Mantém o nível de ameaça e quem é o predador dominante.
    """
    threat_level: int = 1  # 1 (Calmo) a 10 (Apocalíptico)
    
    # O Predador Alpha atual (UUID da Instância). 
    # Se o jogador matá-lo, ganha bônus massivo/achievement.
    current_alpha_uid: Optional[str] = None 
    alpha_title: Optional[str] = None # Título do Alpha (ex: "o Estraçalhador")
    alpha_since: Optional[datetime] = None
    
    # Balança Ecológica
    # Se predator_count cair muito -> prey_count explode
    population_count: int = 0
    
    # Balança de tipos (opcional para futuro)
    population_balance: Dict[str, int] = field(default_factory=lambda: {
        "predator": 0,
        "prey": 0
    })

@dataclass
class Area:
    """
    Representa uma Zona (coleção de salas).
    """
    id: int  # Zone ID (ex: 1, 2, 100)
    name: str
    description: str
    
    # Ecologia da Zona
    ecology: AreaEcology = field(default_factory=AreaEcology)
    
    # Salas pertencentes a esta área (VNUMs)
    room_vnums: List[int] = field(default_factory=list)

    def set_alpha(self, npc_instance):
        """Define um novo Alpha para a região."""
        self.ecology.current_alpha_uid = npc_instance.uid
        self.ecology.alpha_title = npc_instance.full_name
        self.ecology.alpha_since = datetime.utcnow()
        # Aumenta o nível de ameaça da zona
        self.ecology.threat_level += 1

    def get_alpha_uid(self):
        return self.ecology.current_alpha_uid