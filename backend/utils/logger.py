# Configuração de Logging

import logging
import sys
from backend.config.server_config import LOG_LEVEL, LOG_FILE

# Tenta reconfigurar a saída padrão para UTF-8 (Ajuda no Windows)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Configuração dos Handlers
# 1. Arquivo (Forçamos UTF-8 para suportar acentos e símbolos no disco)
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# 2. Console (Terminal)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Configuração Base
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    handlers=[file_handler, stream_handler]
)

logger = logging.getLogger("aeternus")