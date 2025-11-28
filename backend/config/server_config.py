import os

# ==============================================================================
# CONFIGURAÇÃO DO SERVIDOR, BANCO DE DADOS E LOGS
# ==============================================================================

# 1. Diretório Raiz
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 2. Banco de Dados
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "aeternus.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# 3. Configurações de Rede (API HTTP)
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# 4. Configurações TELNET (NOVO)
TELNET_HOST = "0.0.0.0"
TELNET_PORT = 4000

# 5. Configurações de Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.path.join(BASE_DIR, "aeternus.log")

# 6. Debug
DEBUG_MODE = os.getenv("DEBUG", "True").lower() == "true"