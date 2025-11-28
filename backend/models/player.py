# backend/models/player.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class PlayerSettings:
    """Preferências de interface e jogabilidade."""
    brief_mode: bool = False       # Se True, encurta descrições
    compact_combat: bool = False   # Se True, resume o combate
    color_scheme: str = "default"  # Tema de cores ANSI
    screen_width: int = 80         # Para formatação de texto
    auto_loot: bool = False        # Pegar itens automaticamente

@dataclass
class Player:
    """
    A Entidade Mestra. 
    Contém tanto os dados da Conta (Login) quanto a Alma do Personagem (RPG).
    """
    # Identificação & Conta
    id: str  # Mudado para str para acomodar UUID
    username: str
    email: str = "" # Opcional por enquanto
    is_admin: bool = False
    
    # Core RPG (A Alma)
    race: str = "humano"
    player_class: str = "aventureiro"
    level: int = 1
    experience: int = 0
    
    # Estado Volátil (A Vida)
    room_vnum: str = "10001"
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
    
    # Dados Temporais (Preenchidos na criação)
    created_at: datetime = field(default_factory=datetime.now)
    last_login: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_orm(cls, db_player) -> "Player":
        """
        RITUAL DE RESSURREIÇÃO.
        Converte o registro frio do banco (ORM) em um Objeto Vivo.
        """
        # Extrai os atributos JSON do banco (stats)
        attrs = db_player.attributes or {}
        
        return cls(
            # Dados de Identificação
            id=str(db_player.id),
            username=db_player.name,
            
            # Dados de RPG
            race=db_player.race,
            player_class=db_player.player_class,
            level=db_player.level,
            experience=db_player.experience,
            room_vnum=db_player.current_room_vnum,
            
            # Recupera estado vital do JSON
            hp=attrs.get("hp", 100),
            max_hp=attrs.get("max_hp", 100),
            mana=attrs.get("mana", 50),
            max_mana=attrs.get("max_mana", 50),
            
            # Listas
            inventory=db_player.inventory or [],
            equipment=db_player.equipment or {},
            
            # Flags
            is_dead=db_player.is_dead,
            
            # Datas (se disponíveis no ORM, senão usa agora)
            created_at=db_player.created_at or datetime.now(),
            last_login=db_player.updated_at or datetime.now()
        )

    def get_stats_dict(self) -> dict:
        """
        Prepara os dados vitais para serem salvos no campo JSON 'attributes' do banco.
        """
        return {
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mana": self.mana,
            "max_mana": self.max_mana,
            # Configurações também podem ser salvas aqui se quiser
            "settings": {
                "brief_mode": self.settings.brief_mode,
                "auto_loot": self.settings.auto_loot
            }
        }

    def __repr__(self):
        return f"<Player '{self.username}' (Lvl {self.level}) @ {self.room_vnum}>"