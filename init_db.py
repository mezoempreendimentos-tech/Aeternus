import sys
import os

# Adiciona o diretório atual ao path do Python para conseguir importar o backend
sys.path.append(os.getcwd())

from backend.db.base import Base, engine
from backend.db.models import PlayerORM

def init_db():
    print("--- INICIANDO RITUAL DE GÊNESIS ---")
    print(f"Destino do Banco: {engine.url}")
    
    # Isso cria todas as tabelas definidas nos Models (PlayerORM, etc)
    # Se o arquivo aeternus.db não existir, ele cria.
    Base.metadata.create_all(bind=engine)
    
    print("--- TABELAS CRIADAS COM SUCESSO ---")
    print("O mundo de Aeternus agora tem memória.")

if __name__ == "__main__":
    init_db()