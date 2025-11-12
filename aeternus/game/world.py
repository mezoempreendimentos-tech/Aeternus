import os
import yaml
import glob
from pathlib import Path
from aeternus.game.objects.room import Room

class World:
    """
    O Guardião de Toda a Existência.
    Mantém o registro de todas as salas, mobs e itens carregados.
    """
    def __init__(self):
        self.rooms: dict[str, Room] = {} # Mapa: VNUM -> Objeto Room
        
    def load_assets(self):
        """O Grande Ritual de Carregamento."""
        print("🌍 [WORLD] Iniciando a materialização do mundo...")
        self._load_rooms()
        # Futuro: _load_mobs(), _load_items()

    def _load_rooms(self):
        # Busca recursiva por todos os arquivos 'rooms.yaml' dentro de data/world/zones
        search_path = Path("data/world/zones")
        files = list(search_path.rglob("rooms.yaml"))
        
        if not files:
            print("⚠️ [WORLD] Nenhum arquivo de sala encontrado. O universo está vazio?")
            return

        count = 0
        for yaml_file in files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if not data: continue
                    
                    for room_data in data:
                        new_room = Room(room_data)
                        self.rooms[new_room.vnum] = new_room
                        count += 1
            except Exception as e:
                print(f"💀 [ERRO] Falha ao ler {yaml_file}: {e}")

        print(f"🏠 [WORLD] {count} salas foram erguidas da névoa.")

    def get_room(self, vnum: str) -> Room:
        """Retorna a sala pelo VNUM ou a sala do Limbo se não existir."""
        return self.rooms.get(str(vnum))

# Instância Global (Singleton)
# Qualquer lugar do código que importar 'world' terá acesso aos dados.
world = World()