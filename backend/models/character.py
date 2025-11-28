# backend/models/character.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class ResourcePool:
    """Gerencia recursos vitais e flutuantes (HP, Mana, Sanidade)."""
    current: int
    maximum: int
    regen_rate: float

@dataclass
class Attribute:
    """Um dos pilares que sustentam a existência do ser."""
    name: str
    base: int
    modifiers: int = 0
    
    @property
    def total(self) -> int:
        return self.base + self.modifiers

@dataclass
class LifeEvent:
    """
    Um fragmento de memória gravado na alma.
    Estes são os feitos que a Morte lerá em seu livro quando sua hora chegar.
    """
    timestamp: datetime
    event_type: str  # ex: 'KILL_BOSS', 'DISCOVERED_AREA', 'DIED_SHAMEFULLY'
    description: str # ex: "Decapitou o Dragão Azul com uma colher enferrujada"
    importance: int  # 1 (mundano) a 10 (lendário)

@dataclass
class Character:
    """
    A manifestação do jogador no mundo.
    Inclui anatomia, equipamento granular, atributos e o peso de suas memórias.
    """
    id: int
    player_id: int
    name: str
    
    # Identidade
    race_id: str
    class_id: str
    title: str = "o Ninguém"
    
    # Descrição e RP
    short_description: str = "Uma figura indistinta nas sombras."
    bio: str = ""
    
    # Progressão e Ciclo de Vida (Samsara)
    level: int = 1
    experience: int = 0
    
    # Skills ativas nesta encarnação (Lista de VNUMs ou IDs string)
    skills: List[str] = field(default_factory=list)
    
    # Skills herdadas de vidas passadas (Persistem após Remort)
    inherited_skills: List[str] = field(default_factory=list)
    
    # Quantas vezes completou o ciclo
    remort_count: int = 0
    
    # Recursos Vitais (Calculados com base nos Atributos)
    hp: ResourcePool = field(default_factory=lambda: ResourcePool(100, 100, 1.0))
    mana: ResourcePool = field(default_factory=lambda: ResourcePool(50, 50, 0.5))
    stamina: ResourcePool = field(default_factory=lambda: ResourcePool(100, 100, 2.0))
    sanity: ResourcePool = field(default_factory=lambda: ResourcePool(100, 100, 0.1))
    
    # Os 9 Pilares do Ser (Atributos)
    attributes: Dict[str, Attribute] = field(default_factory=lambda: {
        "strength": Attribute("Força", 10),
        "dexterity": Attribute("Destreza", 10),
        "constitution": Attribute("Constituição", 10),
        "intelligence": Attribute("Inteligência", 10),
        "wisdom": Attribute("Sabedoria", 10),
        "charisma": Attribute("Carisma", 10),
        "luck": Attribute("Sorte", 10),
        "perception": Attribute("Percepção", 10),
        "willpower": Attribute("Vontade", 10)
    })
    
    # Diário de Vida
    life_journal: List[LifeEvent] = field(default_factory=list)
    
    # Estatísticas da vida atual (zeradas ao morrer/remort)
    current_life_stats: Dict[str, int] = field(default_factory=lambda: {
        "mobs_killed": 0,
        "damage_dealt": 0,
        "gold_earned": 0,
        "highest_damage_hit": 0
    })

    # Equipamento Granular (Slot -> UUID)
    equipment: Dict[str, Optional[str]] = field(default_factory=lambda: {
        "head": None, "face": None, "eyes": None, "nose": None, "ears": None,
        "neck": None, "shoulders": None, "chest": None, "back": None,
        "arms": None, "wrists": None, "hands": None,
        "waist": None, "legs": None, "feet": None,
        "finger_l": None, "finger_r": None, "insignia": None,
        "main_hand": None, "off_hand": None,
        "light": None, "tool": None
    })
    
    # Anatomia Física
    anatomy: Dict[str, dict] = field(default_factory=dict)
    
    # Estado e Localização
    flags: List[str] = field(default_factory=list)
    location_vnum: int = 1

    def log_event(self, type: str, desc: str, importance: int = 1):
        """Registra um feito na tapeçaria desta vida."""
        self.life_journal.append(LifeEvent(datetime.utcnow(), type, desc, importance))

    def reset_life(self):
        """Chamado na Ressurreição."""
        self.life_journal.clear()
        self.current_life_stats = {k: 0 for k in self.current_life_stats}