#!/usr/bin/env python3
"""
AETERNUS MUD - Project Genesis Script
Cria a estrutura completa de pastas, subpastas e arquivos iniciais
Execução: python3 genesis.py
"""

import os
import json
from pathlib import Path
from typing import List, Dict

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{text.center(60)}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

# ============================================================================
# ESTRUTURA DE PASTAS
# ============================================================================

DIRECTORY_STRUCTURE = {
    "root": {
        "DOCUMENTAÇÃO": {},
        "backend": {
            "config": {},
            "models": {},
            "db": {
                "migrations": {
                    "versions": {}
                }
            },
            "cache": {},
            "handlers": {},
            "game": {
                "engines": {
                    "combat": {},
                    "magic": {},
                    "crafting": {},
                    "skills": {},
                    "movement": {},
                    "ai": {},
                    "economy": {},
                    "events": {}
                },
                "world": {},
                "state": {},
                "utils": {}
            },
            "ai": {},
            "api": {},
            "utils": {}
        },
        "data": {},
        "tests": {
            "engines": {
                "combat": {},
                "magic": {},
                "crafting": {},
                "skills": {}
            },
            "models": {},
            "db": {}
        }
    }
}

# ============================================================================
# ARQUIVOS INICIAIS
# ============================================================================

FILES_TO_CREATE = {
    # Documentação
    "DOCUMENTAÇÃO/GAME_DESIGN.md": """# AETERNUS - Game Design Document

## Visão Geral
Um MUD moderno focado em jogabilidade profunda, IA criativa e economia emergente.

## Características Principais
- Combate baseado em turnos com sistema de iniciativa
- Magia com sistema de mana e efeitos dinâmicos
- Crafting com qualidade baseada em skill
- NPCs com IA generativa (Ollama)
- Sistema econômico com dinâmica de preços
- Áreas procedurais e eventos aleatórios

## Público-alvo
Jogadores hardcore de MUD, faixa etária 20+, interessados em RP imersivo.

## Status
Em desenvolvimento - MVP planejado para Dec 2025
""",

    "DOCUMENTAÇÃO/MECHANICS.md": """# AETERNUS - Mecânicas de Jogo

## Sistemas Principais

### 1. Atributos Base
- **Strength**: Dano físico, carry capacity
- **Dexterity**: Chance de acerto, esquiva, velocidade
- **Intelligence**: Dano mágico, mana pool
- **Wisdom**: Resistência mágica, regeneração
- **Constitution**: HP, resistência a efeitos

### 2. Classe e Raça
- Combinação que define atributos iniciais
- Bônus de skills específicos
- Restrições de equipamento

### 3. Level e Experiência
- Level de 1 a 50
- XP por matar mobs, completar quests, crafting
- Reset possível em later game

## Economia
- Moeda: Gold
- NPCs compram/vendem por preço dinâmico
- Raro tem inflação/deflação procedural

## Tempo
- 1 tick de jogo = 0.5 segundos real
- Ciclo dia/noite de 30 minutos
- Estações mudam a cada 2 horas
""",

    "DOCUMENTAÇÃO/SKILLS.md": """# AETERNUS - Sistema de Habilidades

## Estrutura de Skill
```
{
  "id": "slash",
  "name": "Slash",
  "description": "Um ataque cortante básico",
  "type": "melee",
  "damage_multiplier": 1.0,
  "cooldown": 1.5,
  "mana_cost": 0,
  "requirements": {
    "strength": 10,
    "level": 1
  },
  "effects": []
}
```

## Categorias
- Melee: Ataques próximos
- Ranged: Ataques à distância
- Magic: Feiços
- Utility: Habilidades especiais

## Cooldown
- Tempo mínimo entre usos
- Reduced by haste effects
- Zeroed on certain conditions
""",

    "DOCUMENTAÇÃO/COMBAT_RULES.md": """# AETERNUS - Regras de Combate

## Fluxo de Combate
1. Ambos rolam iniciativa (d20 + DEX modifier)
2. Ordem de turnos estabelecida
3. Cada turno: atacante escolhe ação
4. Defender reage automaticamente ou escolhe ação
5. Loop até morte de um

## Cálculo de Dano
```
base_damage = weapon_damage + (strength * 0.5)
modified_damage = base_damage * skill_multiplier
total_damage = modified_damage - (enemy_armor * 0.2)
final_damage = max(1, total_damage)
```

## Efeitos de Combate
- Bleed: -5 HP/tick por 5 ticks
- Stun: Miss próximo turno
- Haste: +20% speed
- Blind: -30% accuracy

## Morte
- HP atinge 0
- Respawn em última cidade
- Perda de 10% de XP não earned
- Dropar 50% do inventory
""",

    "DOCUMENTAÇÃO/CRAFTING_SYSTEM.md": """# AETERNUS - Sistema de Crafting

## Estrutura de Receita
```
{
  "id": "iron_sword",
  "name": "Iron Sword",
  "materials": {
    "iron_bar": 3,
    "leather": 1
  },
  "skill_required": "blacksmith",
  "skill_level": 10,
  "time": 30,
  "quality_range": [0.5, 1.5]
}
```

## Qualidade
- Baseada em diferença entre skill e dificuldade
- Afeta damage, durability, valor
- Pode gerar items únicos em high quality

## Skills de Crafting
- Blacksmith: Armas e armaduras
- Alchemy: Poções
- Enchanting: Itens mágicos
- Cooking: Comida

## Durability
- Decresce com uso
- Pode ser reparado (custo)
- Item quebrado = inutilizável
""",

    "DOCUMENTAÇÃO/MAGIC_SYSTEM.md": """# AETERNUS - Sistema de Magia

## Estrutura de Feiço
```
{
  "id": "fireball",
  "name": "Fireball",
  "description": "Lança uma bola de fogo",
  "mana_cost": 30,
  "cooldown": 3.0,
  "range": 20,
  "damage": 40,
  "effects": ["burn"],
  "requirements": {
    "intelligence": 15,
    "level": 10
  }
}
```

## Mana
- Pool baseado em Intelligence
- Regenera 5 mana/segundo
- Haste multiplica regeneração

## Spell Schools
- Fire: Damage + Burn
- Ice: Damage + Slow
- Lightning: Damage + Stun
- Healing: Restore HP + Cure

## Resistências
- NPC pode resistir feiços
- Diminui damage em 30-50%
- Podem absorver inteiramente em rare cases
""",

    "DOCUMENTAÇÃO/AI_BEHAVIOR.md": """# AETERNUS - Comportamento de NPCs com IA

## Arquétipos de NPC
1. **Warrior**: Ataca diretamente, comportamento agressivo
2. **Merchant**: Negocia, avesso a combate
3. **Mage**: Usa feiços, mantém distância
4. **Rogue**: Emboscadas, fugas rápidas
5. **Priest**: Heal allies, buffs

## Contexto para Ollama
```
NPC: "Goblin Warrior"
Personality: Aggressive, territorial
Memory: [last 5 interactions]
Current State: Patrolling
Nearby: 1 player approaching
Instruction: Decide next action
```

## Decisões Típicas
- Attack: Enemy nearby
- Patrol: Routine movement
- Dialogue: Player interaction
- Flee: Low HP
- Heal: Ally damaged

## Fallback Behaviors
Se Ollama falhar:
- Comportamento baseado em regras
- Estado anterior + noise
- Sempre garantido uma ação válida

## Emotes Periódicos
A cada 30-60s, NPC faz emote (via Ollama background)
- "Goblin yawns"
- "Merchant counts coins"
- "Mage mutters arcane words"
""",

    "DOCUMENTAÇÃO/WORLD_MAP.md": """# AETERNUS - Mapa do Mundo

## Estrutura de Áreas
```
The Shattered Isles
├── Starter Zone (Level 1-10)
│   ├── Village Square
│   ├── Training Grounds
│   └── Goblin Caves
├── Forest Region (Level 10-20)
│   ├── Dark Woods
│   ├── Druid Grove
│   └── Bandit Camp
└── Dungeons
    ├── Crystal Cavern (Level 15-25)
    ├── Haunted Manor (Level 25-35)
    └── Dragon's Lair (Level 45-50)
```

## Room Template
```
{
  "id": "village_square",
  "title": "Village Square",
  "description": "A bustling plaza with merchants and adventurers",
  "area": "starter_zone",
  "exits": {
    "north": "training_grounds",
    "south": "tavern",
    "east": "market"
  },
  "spawns": [
    {"npc_id": "merchant", "count": 2, "respawn_time": 300}
  ]
}
```

## Conectividade
- Rooms formam grafo conectado
- Alguns exits requerem password/key
- Boss rooms isoladas
""",

    "DOCUMENTAÇÃO/ECONOMY.md": """# AETERNUS - Sistema Econômico

## Preços Base
- Item raro: 100-500 gold
- Comum: 10-100 gold
- Junk: 1-10 gold

## Dinâmica de Preços
- Supply/Demand procedural
- NPCs vendem mais caro se item raro
- Compram mais barato se muita quantidade

## NPCs Traders
- Merchant: Compra/vende items
- Blacksmith: Vende weapons/armor
- Alchemist: Poções
- Fence: Items roubados (low value)

## Economia de Player
- No auction house inicial
- Trading direto P2P
- NPCs como intermediários

## Inflação/Deflação
- Mob drops geram inflação
- Crafting materiais geram deflação
- Rebalancing automático
""",

    "DOCUMENTAÇÃO/ECONOMY.md": """# AETERNUS - Sistema Econômico

## Preços Base
- Item raro: 100-500 gold
- Comum: 10-100 gold
- Junk: 1-10 gold

## Dinâmica de Preços
- Supply/Demand procedural
- NPCs vendem mais caro se item raro
- Compram mais barato se muita quantidade

## NPCs Traders
- Merchant: Compra/vende items
- Blacksmith: Vende weapons/armor
- Alchemist: Poções
- Fence: Items roubados (low value)

## Economia de Player
- No auction house inicial
- Trading direto P2P
- NPCs como intermediários

## Inflação/Deflação
- Mob drops geram inflação
- Crafting materiais geram deflação
- Rebalancing automático
""",

    # Backend - Config
    "backend/config/__init__.py": "",
    
    "backend/config/game_config.py": """# Configurações de Jogo AETERNUS

GAME_CONSTANTS = {
    "MAX_LEVEL": 50,
    "BASE_HEALTH": 100,
    "BASE_MANA": 50,
    "MANA_REGEN_RATE": 5,  # por segundo
    "COMBAT_TICK": 0.5,    # segundos
    "NPC_DECISION_INTERVAL": (10, 30),  # random entre isso
    "WORLD_TICK": 1.0,     # tick do mundo
    "SESSION_TIMEOUT": 1800,  # 30 minutos inativo
}

CLASS_STATS = {
    "warrior": {
        "strength": 12,
        "dexterity": 10,
        "intelligence": 8,
        "wisdom": 10,
        "constitution": 13,
    },
    "mage": {
        "strength": 8,
        "dexterity": 10,
        "intelligence": 14,
        "wisdom": 12,
        "constitution": 9,
    },
    "rogue": {
        "strength": 10,
        "dexterity": 14,
        "intelligence": 10,
        "wisdom": 11,
        "constitution": 10,
    },
    "priest": {
        "strength": 10,
        "dexterity": 11,
        "intelligence": 12,
        "wisdom": 14,
        "constitution": 11,
    },
}

RACE_BONUSES = {
    "human": {"all": 0},
    "elf": {"dexterity": 2, "intelligence": 1},
    "dwarf": {"constitution": 2, "strength": 1},
    "halfling": {"dexterity": 3, "strength": -1},
}
""",

    "backend/config/server_config.py": """# Configurações de Servidor

import os
from dotenv import load_dotenv

load_dotenv()

# FastAPI
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False") == "True"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/aeternus")
SQLALCHEMY_ECHO = DEBUG

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_CACHE_TTL = 3600  # 1 hora

# Ollama
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
OLLAMA_TIMEOUT = 30  # segundos

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/aeternus.log")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Game
MAX_PLAYERS_ONLINE = 100
TICK_RATE = 20  # ticks per second
""",

    "backend/config/balance.py": """# Balanceamento de Jogo

# Combate
COMBAT_DAMAGE_MULTIPLIER = 1.2
CRITICAL_CHANCE = 0.15  # 15%
CRITICAL_MULTIPLIER = 2.0

# Defesa
ARMOR_REDUCTION_FACTOR = 0.2
DODGE_CHANCE_MULTIPLIER = 0.1

# Magia
SPELL_DAMAGE_MULTIPLIER = 1.0
MANA_COST_MULTIPLIER = 1.0
SPELL_COOLDOWN_BASE = 1.0

# Crafting
CRAFTING_TIME_MULTIPLIER = 1.0
CRAFTING_XP_MULTIPLIER = 1.5
QUALITY_SUCCESS_THRESHOLD = 0.7

# Economia
BASE_NPC_SELL_PRICE = 100
NPC_BUY_PERCENTAGE = 0.5  # NPCs compram por 50% do valor
INFLATION_RATE = 0.01  # 1% por semana

# IA
OLLAMA_TIMEOUT_SECONDS = 5
OLLAMA_CONTEXT_LENGTH = 500
DIALOGUE_CACHE_TTL = 3600  # 1 hora

# Rewards
MOB_KILL_XP_BASE = 100
QUEST_XP_MULTIPLIER = 2.0
CRAFTING_XP_BASE = 50
""",

    "backend/config/constants.py": """# Constantes Globais

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
""",

    # Backend - Models
    "backend/models/__init__.py": "",
    
    "backend/models/player.py": """# Modelo de Jogador

from dataclasses import dataclass
from typing import Optional

@dataclass
class Player:
    id: int
    username: str
    created_at: str
    last_login: str
    active_character_id: Optional[int] = None
""",

    "backend/models/character.py": """# Modelo de Personagem

from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Character:
    id: int
    player_id: int
    name: str
    class_type: str  # warrior, mage, etc
    race: str  # human, elf, etc
    level: int = 1
    experience: int = 0
    hp: int = 100
    mana: int = 50
    
    # Atributos
    strength: int = 10
    dexterity: int = 10
    intelligence: int = 10
    wisdom: int = 10
    constitution: int = 10
    
    # Estado
    location_id: int = 1  # Room ID
    inventory: List[Dict] = field(default_factory=list)
    equipped: Dict = field(default_factory=dict)
    
    # Progression
    skills: Dict[str, int] = field(default_factory=dict)
    quests: List[int] = field(default_factory=list)
""",

    "backend/models/item.py": """# Modelo de Item

from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class Item:
    id: int
    template_id: str
    owner_id: Optional[int]  # None se no ground
    location_id: int  # Room ID se no ground
    quantity: int = 1
    durability: int = 100
    properties: Dict = None
""",

    "backend/models/npc.py": """# Modelo de NPC

from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class NPC:
    id: int
    template_id: str
    name: str
    level: int
    location_id: int
    
    # Estado
    hp: int
    max_hp: int
    state: str  # idle, patrolling, aggro, talking
    
    # IA
    personality: str  # aggressive, friendly, neutral
    memory: List[Dict] = field(default_factory=list)
    last_action_time: float = 0
    
    # Skills
    skills: List[str] = field(default_factory=list)
    
    # Loot
    loot_table: Dict = field(default_factory=dict)
""",

    "backend/models/room.py": """# Modelo de Room/Sala

from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Room:
    id: int
    area_id: int
    title: str
    description: str
    exits: Dict[str, int] = field(default_factory=dict)  # north: room_id
    players_here: List[int] = field(default_factory=list)
    npcs_here: List[int] = field(default_factory=list)
    items_here: List[int] = field(default_factory=list)
""",

    # Backend - DB
    "backend/db/__init__.py": "",
    
    "backend/db/base.py": """# Configuração SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config.server_config import DATABASE_URL, SQLALCHEMY_ECHO

# Engine
engine = create_engine(DATABASE_URL, echo=SQLALCHEMY_ECHO)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para models ORM
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",

    "backend/db/models.py": """# Modelos ORM SQLAlchemy para PostgreSQL

from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.base import Base
from datetime import datetime

class PlayerORM(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    
    characters = relationship("CharacterORM", back_populates="player")

class CharacterORM(Base):
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    name = Column(String, unique=True)
    class_type = Column(String)
    race = Column(String)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    hp = Column(Integer, default=100)
    mana = Column(Integer, default=50)
    
    # Atributos (JSONB)
    attributes = Column(JSON, default={
        "strength": 10,
        "dexterity": 10,
        "intelligence": 10,
        "wisdom": 10,
        "constitution": 10
    })
    
    location_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    player = relationship("PlayerORM", back_populates="characters")

class ItemORM(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True)
    template_id = Column(String)
    owner_id = Column(Integer, ForeignKey("characters.id"), nullable=True)
    location_id = Column(Integer, nullable=True)  # Room ID se no ground
    quantity = Column(Integer, default=1)
    durability = Column(Integer, default=100)
    properties = Column(JSON, default={})

class RoomORM(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True)
    area_id = Column(Integer)
    title = Column(String)
    description = Column(String)
    exits = Column(JSON, default={})
    properties = Column(JSON, default={})

class NPCORM(Base):
    __tablename__ = "npcs"
    
    id = Column(Integer, primary_key=True)
    template_id = Column(String)
    name = Column(String)
    level = Column(Integer)
    location_id = Column(Integer)
    hp = Column(Integer)
    max_hp = Column(Integer)
    
    personality = Column(String)
    ai_profile = Column(JSON, default={})
    loot_table = Column(JSON, default={})
    memory = Column(JSON, default=[])

class SkillORM(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True)
    skill_id = Column(String, unique=True)
    name = Column(String)
    damage = Column(Float, default=0)
    cooldown = Column(Float, default=0)
    mana_cost = Column(Integer, default=0)
    requirements = Column(JSON, default={})
""",

    "backend/db/queries.py": """# Queries Reutilizáveis

from sqlalchemy.orm import Session
from backend.db.models import PlayerORM, CharacterORM, ItemORM, RoomORM, NPCORM

async def get_player_by_username(db: Session, username: str):
    return db.query(PlayerORM).filter(PlayerORM.username == username).first()

async def get_character_by_id(db: Session, char_id: int):
    return db.query(CharacterORM).filter(CharacterORM.id == char_id).first()

async def get_character_inventory(db: Session, char_id: int):
    return db.query(ItemORM).filter(ItemORM.owner_id == char_id).all()

async def get_room_by_id(db: Session, room_id: int):
    return db.query(RoomORM).filter(RoomORM.id == room_id).first()

async def get_npc_by_id(db: Session, npc_id: int):
    return db.query(NPCORM).filter(NPCORM.id == npc_id).first()

async def get_npcs_in_location(db: Session, location_id: int):
    return db.query(NPCORM).filter(NPCORM.location_id == location_id).all()
""",

    "backend/cache/__init__.py": "",
    
    "backend/cache/redis_client.py": """# Cliente Redis

import redis.asyncio as redis
from backend.config.server_config import REDIS_URL

class RedisClient:
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        self.redis = await redis.from_url(REDIS_URL)
    
    async def disconnect(self):
        await self.redis.close()
    
    async def get(self, key: str):
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, ex: int = None):
        await self.redis.set(key, value, ex=ex)
    
    async def delete(self, key: str):
        await self.redis.delete(key)
    
    async def publish(self, channel: str, message: str):
        await self.redis.publish(channel, message)
""",

    # Backend - Game
    "backend/game/__init__.py": "",
    "backend/game/engines/__init__.py": "",
    "backend/game/world/__init__.py": "",
    "backend/game/state/__init__.py": "",
    "backend/game/utils/__init__.py": "",

    # Backend - Game Engines
    "backend/game/engines/combat/__init__.py": "",
    "backend/game/engines/magic/__init__.py": "",
    "backend/game/engines/crafting/__init__.py": "",
    "backend/game/engines/skills/__init__.py": "",
    "backend/game/engines/movement/__init__.py": "",
    "backend/game/engines/ai/__init__.py": "",
    "backend/game/engines/economy/__init__.py": "",
    "backend/game/engines/events/__init__.py": "",

    "backend/game/engines/combat/combat.py": """# Motor de Combate - Orquestrador

class CombatEngine:
    def __init__(self):
        pass
    
    async def start_combat(self, attacker_id, defender_id):
        \"\"\"Inicia combate entre dois participants\"\"\"
        pass
    
    async def execute_action(self, attacker_id, action):
        \"\"\"Executa ação de um participant\"\"\"
        pass
    
    def calculate_damage(self, attacker, defender, skill):
        \"\"\"Calcula dano (pura lógica, sem I/O)\"\"\"
        pass
""",

    "backend/game/engines/combat/db_interface.py": """# Motor de Combate - Interface com BD

# Única arquivo que acessa BD/Cache para combate

async def get_attacker(db, attacker_id):
    pass

async def get_defender(db, defender_id):
    pass

async def save_combat_state(cache, combat_id, state):
    pass

async def update_character_hp(db, char_id, new_hp):
    pass
""",

    # Backend - AI
    "backend/ai/__init__.py": "",
    
    "backend/ai/ollama_service.py": """# Serviço Ollama - Wrapper

import httpx
from backend.config.server_config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT

class OllamaService:
    def __init__(self):
        self.host = OLLAMA_HOST
        self.model = OLLAMA_MODEL
        self.timeout = OLLAMA_TIMEOUT
    
    async def generate(self, prompt: str, context: str = "") -> str:
        \"\"\"Gera texto via Ollama\"\"\"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "context": context
                },
                timeout=self.timeout
            )
            return response.json()["response"]
""",

    # Backend - API
    "backend/api/__init__.py": "",
    
    "backend/api/routes.py": """# Rotas FastAPI

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "game": "AETERNUS"}

@router.post("/auth/register")
async def register(username: str, password: str):
    pass

@router.post("/auth/login")
async def login(username: str, password: str):
    pass

@router.get("/characters")
async def list_characters(player_id: int):
    pass

@router.post("/characters")
async def create_character(player_id: int, name: str, class_type: str, race: str):
    pass
""",

    "backend/api/websocket.py": """# WebSocket Endpoint

from fastapi import WebSocket

async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process data
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
""",

    # Backend - Handlers
    "backend/handlers/__init__.py": "",
    
    "backend/handlers/command_handler.py": """# Manipulador de Comandos

class CommandHandler:
    def __init__(self, game_engine):
        self.game_engine = game_engine
    
    async def handle_command(self, player_id, command_text):
        \"\"\"Parse e roteia comando para motor apropriado\"\"\"
        parts = command_text.split()
        cmd = parts[0].lower()
        args = parts[1:]
        
        # Router
        if cmd == "attack":
            pass
        elif cmd == "talk":
            pass
        elif cmd == "move":
            pass
""",

    # Backend - Utils
    "backend/utils/__init__.py": "",
    
    "backend/utils/logger.py": """# Configuração de Logging

import logging
from backend.config.server_config import LOG_LEVEL, LOG_FILE

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("aeternus")
""",

    # Backend - Main
    "backend/main.py": """# Main - Servidor FastAPI

import asyncio
from fastapi import FastAPI
from backend.api.routes import router
from backend.cache.redis_client import RedisClient
from backend.utils.logger import logger

app = FastAPI(title="AETERNUS MUD")

# Redis
redis_client = RedisClient()

@app.on_event("startup")
async def startup():
    logger.info("Starting AETERNUS MUD...")
    await redis_client.connect()
    logger.info("Redis connected")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down AETERNUS MUD...")
    await redis_client.disconnect()

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
""",

    "backend/requirements.txt": """fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
python-dotenv==1.0.0
httpx==0.25.1
pydantic==2.4.2
pytest==7.4.3
pytest-asyncio==0.21.1
""",

    # Data - JSON
    "data/classes.json": """{
  "warrior": {
    "description": "A strong melee fighter",
    "base_attributes": {
      "strength": 12,
      "dexterity": 10,
      "intelligence": 8,
      "wisdom": 10,
      "constitution": 13
    }
  },
  "mage": {
    "description": "Master of arcane magic",
    "base_attributes": {
      "strength": 8,
      "dexterity": 10,
      "intelligence": 14,
      "wisdom": 12,
      "constitution": 9
    }
  }
}""",

    "data/races.json": """{
  "human": {
    "description": "Versatile and adaptable",
    "bonuses": {}
  },
  "elf": {
    "description": "Graceful and wise",
    "bonuses": {
      "dexterity": 2,
      "intelligence": 1
    }
  }
}""",

    "data/items.json": """{}""",
    "data/skills.json": """{}""",
    "data/spells.json": """{}""",
    "data/recipes.json": """{}""",
    "data/areas.json": """{}""",
    "data/rooms.json": """{}""",
    "data/npcs.json": """{}""",
    "data/quests.json": """{}""",

    # Root
    ".env.example": """# Configurações

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Database
DATABASE_URL=postgresql://aeternus:password@localhost:5432/aeternus

# Redis
REDIS_URL=redis://localhost:6379/0

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/aeternus.log

# Security
SECRET_KEY=your-secret-key-change-me
""",

    ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local

# Logs
logs/
*.log

# Database
*.db
*.sqlite

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
""",

    "docker-compose.yml": """version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: aeternus
      POSTGRES_PASSWORD: password
      POSTGRES_DB: aeternus
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aeternus"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    environment:
      OLLAMA_HOST: 0.0.0.0:11434
    volumes:
      - ollama_data:/root/.ollama

volumes:
  postgres_data:
  ollama_data:
""",

    "README.md": """# AETERNUS MUD

Um MUD (Multi-User Dungeon) moderno construído com:
- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL + Redis
- **IA**: Ollama (Llama 3.2 7B)
- **WebSocket**: Socket.io para tempo real

## Estrutura do Projeto

```
aeternus/
├── DOCUMENTAÇÃO/          # Game Design Documents
├── backend/               # Código do servidor
│   ├── game/engines/      # Motores modulares
│   ├── db/                # ORM e queries
│   ├── config/            # Configurações
│   ├── api/               # Endpoints
│   └── main.py            # Entry point
├── data/                  # Dados do jogo (JSON)
├── tests/                 # Testes
└── docker-compose.yml     # Orquestração
```

## Quick Start

```bash
# 1. Clone repo
git clone https://github.com/seu-usuario/aeternus.git
cd aeternus

# 2. Setup
cp .env.example .env
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 3. Start services
docker-compose up -d

# 4. Run server
python3 backend/main.py
```

## Arquitetura

- **Engines**: Motores modulares (combate, magia, crafting, IA, etc)
- **Models**: Representação de dados do jogo
- **DB**: Camada de persistência
- **Cache**: Estado em tempo real
- **IA**: Integração com Ollama para NPCs

## Documentação

Leia `DOCUMENTAÇÃO/` para game design completo.

## Desenvolvimento

- Use `backend/game/engines/` para adicionar novas features
- Configure em `backend/config/balance.py`
- Dados em `data/` (JSONs)
- Testes em `tests/`

## Status

🚧 Em desenvolvimento - MVP Q4 2025

## Autor

Desenvolvido como projeto de nicho MUD moderno.
""",

    "pytest.ini": """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
"""
}

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def create_directory_structure(base_path: str, structure: Dict, current_path: str = ""):
    """Recursivamente cria pastas"""
    for name, content in structure.items():
        if name == "root":
            create_directory_structure(base_path, content, base_path)
        else:
            new_path = os.path.join(current_path, name)
            if isinstance(content, dict) and not any(k == name for k in FILES_TO_CREATE):
                # É uma pasta
                os.makedirs(new_path, exist_ok=True)
                print_success(f"Pasta: {new_path}")
                create_directory_structure(base_path, content, new_path)

def create_files(base_path: str):
    """Cria todos os arquivos"""
    for file_path, content in FILES_TO_CREATE.items():
        full_path = os.path.join(base_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        print_success(f"Arquivo: {file_path}")

def create_logs_directory(base_path: str):
    """Cria diretório de logs"""
    logs_path = os.path.join(base_path, "logs")
    os.makedirs(logs_path, exist_ok=True)
    print_success(f"Pasta: logs/")

def main():
    print_header("⚔️  AETERNUS MUD - PROJECT GENESIS ⚔️")
    
    # Detectar diretório
    base_path = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(base_path) != "aeternus":
        base_path = os.path.join(base_path, "aeternus")
    
    print_info(f"Criando projeto em: {base_path}")
    
    # Criar pastas
    print_header("📁 CRIANDO ESTRUTURA DE PASTAS")
    create_directory_structure(base_path, DIRECTORY_STRUCTURE)
    
    # Criar logs
    print_header("📝 CRIANDO DIRETÓRIO DE LOGS")
    create_logs_directory(base_path)
    
    # Criar arquivos
    print_header("📄 CRIANDO ARQUIVOS")
    create_files(base_path)
    
    # Resumo final
    print_header("✨ AETERNUS GENESIS CONCLUÍDO ✨")
    print_info(f"Projeto criado em: {base_path}")
    print_info(f"Próximos passos:")
    print(f"  1. cd {base_path}")
    print(f"  2. cp .env.example .env")
    print(f"  3. python3 -m venv venv")
    print(f"  4. source venv/bin/activate")
    print(f"  5. pip install -r backend/requirements.txt")
    print(f"  6. docker-compose up -d")
    print(f"  7. python3 backend/main.py")
    print()

if __name__ == "__main__":
    main()
