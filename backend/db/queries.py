from sqlalchemy.orm import Session
from backend.db.models import PlayerORM
import uuid

# ==============================================================================
# QUERIES (LEITURA E ESCRITA)
# ==============================================================================

def get_player_by_name(db: Session, name: str):
    """
    Busca um jogador pelo nome. Retorna None se não existir.
    """
    return db.query(PlayerORM).filter(PlayerORM.name == name).first()

def get_player_by_id(db: Session, player_id: str):
    """
    Busca um jogador pelo UUID.
    """
    return db.query(PlayerORM).filter(PlayerORM.id == player_id).first()

def create_player(db: Session, name: str, race: str, p_class: str) -> PlayerORM:
    """
    Cria um novo jogador no banco de dados com valores iniciais padrão.
    """
    # Gera um ID novo
    new_id = str(uuid.uuid4())
    
    # Cria o objeto
    db_player = PlayerORM(
        id=new_id,
        name=name,
        race=race,
        player_class=p_class,
        level=1,
        experience=0,
        current_room_vnum="10001",
        attributes={"hp": 100, "max_hp": 100, "mana": 50, "max_mana": 50},
        inventory=[],
        equipment={}
    )
    
    # Adiciona na sessão e salva (commit)
    db.add(db_player)
    db.commit()
    
    # Atualiza o objeto com os dados salvos (ex: datas automáticas)
    db.refresh(db_player)
    
    return db_player

def save_player_state(db: Session, player_id: str, room_vnum: str, stats: dict, level: int, xp: int):
    """
    Atualiza um jogador existente com os dados atuais da memória.
    """
    player = db.query(PlayerORM).filter(PlayerORM.id == player_id).first()
    
    if player:
        player.current_room_vnum = room_vnum
        player.attributes = stats
        player.level = level
        player.experience = xp
        # Adicionar inventário aqui depois
        
        db.commit()
        db.refresh(player)
        return player
    return None