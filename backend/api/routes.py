# Rotas FastAPI

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
