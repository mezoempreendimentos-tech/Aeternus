import json
import os
from pathlib import Path
from aeternus.core.config import settings
from aeternus.game.objects.player import Player

class Storage:
    """
    O Guardião dos Registos. Responsável por salvar e carregar JSONs de jogadores.
    """
    def __init__(self):
        # Pasta onde os saves ficam: data/players/
        self.player_dir = settings.DATA_DIR / "players"
        self.player_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, player_name: str) -> Path:
        # Normaliza nome para minusculo: 'Conan' -> 'conan.json'
        clean_name = player_name.lower().strip()
        return self.player_dir / f"{clean_name}.json"

    def player_exists(self, player_name: str) -> bool:
        return self._get_file_path(player_name).exists()

    def save_player(self, player: Player):
        """Grava a alma no disco."""
        if not player: return
        
        file_path = self._get_file_path(player.name)
        data = player.to_dict()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 [STORAGE] Jogador {player.name} salvo com sucesso.")
        except Exception as e:
            print(f"💀 [ERRO] Falha ao salvar {player.name}: {e}")

    def load_player(self, player_name: str) -> Player:
        """Ressuscita a alma do disco."""
        file_path = self._get_file_path(player_name)
        
        if not file_path.exists():
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cria um corpo vazio
            player = Player(data["name"])
            # Injeta a alma (dados)
            player.load_from_dict(data)
            
            return player
        except Exception as e:
            print(f"💀 [ERRO] Falha ao carregar {player_name}: {e}")
            return None

# Instância Global
storage = Storage()