import os
import yaml
from pathlib import Path
from aeternus.game.objects.room import Room
from aeternus.game.objects.item import Item
from aeternus.game.objects.mob import Mob
from aeternus.core.config import settings

class World:
    def __init__(self):
        self.room_blueprints: dict[str, Room] = {}
        self.item_blueprints: dict[str, Item] = {}
        self.mob_blueprints: dict[str, Mob] = {}
        
        self.active_players: list = [] # Lista de Jogadores Online

    def load_assets(self):
        print("🌍 [WORLD] Carregando ativos...")
        self._load_generic("rooms.yaml", Room, self.room_blueprints, "Salas")
        self._load_generic("items.yaml", Item, self.item_blueprints, "Itens")
        self._load_generic("mobs.yaml", Mob, self.mob_blueprints, "Criaturas")

    def _load_generic(self, filename, class_ref, target_dict, label):
        search_path = settings.ZONES_DIR
        files = list(search_path.rglob(filename))
        if not files: return
        count = 0
        for yaml_file in files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if not data: continue
                    if isinstance(data, dict): data = [data]
                    for entry in data:
                        obj = class_ref(entry)
                        target_dict[obj.vnum] = obj
                        count += 1
            except: pass
        print(f"📦 [WORLD] {count} {label} carregados.")

    def get_room(self, vnum: str) -> Room:
        return self.room_blueprints.get(str(vnum))

    def create_item(self, vnum: str) -> Item:
        return self.item_blueprints.get(str(vnum))

    def create_mob(self, vnum: str) -> Mob:
        return self.mob_blueprints.get(str(vnum))

    # --- GESTÃO DE JOGADORES ---
    def add_player(self, player):
        if player not in self.active_players:
            self.active_players.append(player)
            print(f"➕ [WORLD] {player.name} adicionado à lista global. Total: {len(self.active_players)}")

    def remove_player(self, player):
        if player in self.active_players:
            self.active_players.remove(player)
            print(f"➖ [WORLD] {player.name} removido da lista global.")

world = World()