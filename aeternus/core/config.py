import os
from pathlib import Path

class Settings:
    """
    Configuração Central do Aeternus.
    Versão Leve (Zero Dependências) para compatibilidade com Cygwin.
    """
    def __init__(self):
        # 1. Tenta carregar o arquivo .env manualmente
        self.BASE_DIR = Path(__file__).resolve().parent.parent.parent
        self._load_env_file(self.BASE_DIR / ".env")

        # 2. Define as variáveis (lendo do ambiente ou usando padrão)
        
        # --- Rede ---
        self.SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
        self.SERVER_PORT = int(os.getenv("SERVER_PORT", 4000))
        self.MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", 100))
        
        # --- Caminhos ---
        self.DATA_DIR = self.BASE_DIR / "data"
        self.BLUEPRINTS_DIR = self.DATA_DIR / "blueprints"
        self.ZONES_DIR = self.DATA_DIR / "world" / "zones"
        
        # --- Jogo ---
        self.GAME_NAME = os.getenv("GAME_NAME", "Aeternus MUD")
        self.START_ROOM_VNUM = os.getenv("START_ROOM_VNUM", "3001")
        self.DEFAULT_RESPAWN_TIME = int(os.getenv("DEFAULT_RESPAWN_TIME", 15))
        
        # --- Sistema ---
        self.DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    def _load_env_file(self, env_path):
        """Lê um arquivo .env simples linha por linha."""
        if not env_path.exists():
            return
        
        print(f"⚙️ Carregando configurações de: {env_path}")
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    
                    key, value = line.split("=", 1)
                    # Remove aspas se houver
                    value = value.strip().strip("'").strip('"')
                    os.environ[key.strip()] = value
        except Exception as e:
            print(f"⚠️ Erro lendo .env: {e}")

# Instância global
settings = Settings()

# Validação básica
if not settings.DATA_DIR.exists():
    print(f"⚠️ AVISO: Pasta de dados não encontrada em {settings.DATA_DIR}")