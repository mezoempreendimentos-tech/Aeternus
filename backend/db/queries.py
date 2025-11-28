# backend/db/queries.py
from sqlalchemy.orm import Session
from backend.db.models import PlayerORM
import uuid

def get_player_by_name(db: Session, name: str):
    return db.query(PlayerORM).filter(PlayerORM.name == name).first()

def get_player_by_id(db: Session, player_id: str):
    return db.query(PlayerORM).filter(PlayerORM.id == player_id).first()

# CORREÇÃO: Adicionado parâmetro 'password'
def create_player(db: Session, name: str, race: str, p_class: str, password: str = "") -> PlayerORM:
    """
    Cria um novo jogador.
    Agora salva a senha (hash) no banco.
    """
    new_id = str(uuid.uuid4())
    
    db_player = PlayerORM(
        id=new_id,
        name=name,
        password_hash=password, # Salvando a senha (futuramente: usar hash real)
        race=race,
        player_class=p_class,
        level=1,
        experience=0,
        current_room_vnum="10001",
        attributes={"hp": 100, "max_hp": 100},
        inventory=[], 
        equipment={}
    )
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def save_player_state(db: Session, player_id: str, location_vnum: str, stats: dict, level: int, xp: int, inventory_data: list):
    player = db.query(PlayerORM).filter(PlayerORM.id == player_id).first()
    
    if player:
        player.current_room_vnum = str(location_vnum)
        player.attributes = stats
        player.level = level
        player.experience = xp
        player.inventory = inventory_data 
        
        db.commit()
        db.refresh(player)
        return player
    return None