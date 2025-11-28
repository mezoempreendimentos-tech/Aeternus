from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

# Imports do Aeternus
from backend.db.base import get_db
from backend.db.queries import get_player_by_name, create_player
from backend.models.player import Player
from backend.game.world.world_manager import WorldManager

router = APIRouter()

# --- Esquemas de Dados ---
class RegisterRequest(BaseModel):
    username: str
    password: str 
    race: str = "humano"

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str 
    player_id: str
    message: str

# --- Rotas de Autenticação ---

@router.post("/auth/register", response_model=LoginResponse)
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Cria um novo registro."""
    
    if get_player_by_name(db, req.username):
        raise HTTPException(status_code=400, detail="Este nome já pertence a outra lenda.")

    try:
        # CORREÇÃO: Passando req.password
        db_player = create_player(db, req.username, req.race, "novice", password=req.password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha no ritual de criação: {str(e)}")

    return {
        "token": str(db_player.id),
        "player_id": str(db_player.id),
        "message": "Alma criada. Você nasce como um simples Novato."
    }

@router.post("/auth/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Busca a alma no Banco."""
    db_player = get_player_by_name(db, req.username)
    if not db_player:
        raise HTTPException(status_code=404, detail="Alma não encontrada.")
    
    # CORREÇÃO: Verificação simples de senha
    if db_player.password_hash and db_player.password_hash != req.password:
        raise HTTPException(status_code=401, detail="Senha incorreta.")
    
    return {
        "token": str(db_player.id),
        "player_id": str(db_player.id),
        "message": "Login realizado."
    }

@router.get("/health")
async def health_check():
    return {"status": "online", "game": "AETERNUS", "version": "0.8.3"}