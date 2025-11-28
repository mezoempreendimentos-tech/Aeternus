from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from backend.db.base import Base
import uuid

# ==============================================================================
# MODELOS ORM (TABELAS)
# ==============================================================================

class PlayerORM(Base):
    """
    Tabela 'players': Onde as almas dos heróis descansam.
    """
    __tablename__ = "players"

    # -- Identificação --
    # ID único (UUID) convertido para string
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    # Nome do personagem (deve ser único)
    name = Column(String, unique=True, index=True, nullable=False)
    # Senha hashada (FUTURO: por enquanto pode ser nulo ou texto simples para testes)
    password_hash = Column(String, nullable=True)

    # -- Dados Core --
    race = Column(String, default="humano")
    player_class = Column(String, default="aventureiro")
    
    # -- Progressão --
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    
    # -- Localização --
    # VNUM da sala onde o jogador deslogou (Salva o progresso geográfico)
    current_room_vnum = Column(String, default="10001")
    
    # -- Estado Flexível --
    # Aqui guardamos HP, Mana, Stamina, Força, Destreza, etc.
    # Exemplo: {"hp": 100, "max_hp": 100, "str": 10, "inventory_slots": 20}
    attributes = Column(JSON, default={})
    
    # -- Inventário e Equipamento --
    # Listas de IDs ou objetos JSON representando itens
    inventory = Column(JSON, default=[])
    equipment = Column(JSON, default={})

    # -- Meta-dados --
    is_dead = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<PlayerORM(id={self.id}, name={self.name}, level={self.level})>"