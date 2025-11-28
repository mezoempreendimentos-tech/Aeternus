import os

# ==============================================================================
# CONFIGURAÇÃO DO SERVIDOR E BANCO DE DADOS
# ==============================================================================

# Define onde o arquivo do banco de dados será salvo.
# Por padrão, cria um arquivo 'aeternus.db' na pasta raiz do projeto.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "aeternus.db")

# Se houver uma variável de ambiente, usa ela. Senão, usa o arquivo local sqlite.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# Configurações de Rede (caso precise no futuro)
HOST = "0.0.0.0"
PORT = 8000

# Constantes de Debug
DEBUG_MODE = True