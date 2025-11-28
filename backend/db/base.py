from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config.server_config import DATABASE_URL

# ==============================================================================
# INFRAESTRUTURA DO BANCO DE DADOS (SQLALCHEMY)
# ==============================================================================

# 1. Configurar o argumento específico para SQLite
# (SQLite precisa de check_same_thread=False para funcionar com múltiplos usuários)
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

# 2. Criar o "Motor" (Engine) que fala com o banco
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    # echo=True faz o terminal mostrar os comandos SQL (bom para debug)
    echo=False 
)

# 3. Criar a Fábrica de Sessões
# Cada vez que um jogador faz algo, abrimos uma "SessionLocal"
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Criar a Classe Base
# Todos os modelos (tabelas) vão herdar desta classe
Base = declarative_base()

# 5. Função Utilitária para Dependências (FastAPI)
def get_db():
    """
    Cria uma sessão de banco de dados e garante que ela feche
    mesmo se der erro. Use isso nas rotas da API.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()