import os
import yaml
import random
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
        self.zone_resets: list = []
        self.active_players: list = [] 

    def load_assets(self):
        print("🌍 [WORLD] Iniciando a Gênese...")
        self._load_generic("rooms.yaml", Room, self.room_blueprints, "Salas")
        self._load_generic("items.yaml", Item, self.item_blueprints, "Itens")
        self._load_generic("mobs.yaml", Mob, self.mob_blueprints, "Criaturas")
        self._load_resets()
        
        print("⚡ [WORLD] Invocando a vida nas zonas (Populating)...")
        self.populate_world()

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
                        # Força VNUM para string para evitar erros de int/str
                        vnum = str(entry.get('vnum'))
                        obj = class_ref(entry)
                        target_dict[vnum] = obj
                        count += 1
            except: pass
        print(f"📦 [WORLD] {count} {label} carregados.")

    def _load_resets(self):
        files = list(settings.ZONES_DIR.rglob("resets.yaml"))
        count = 0
        for yaml_file in files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data:
                        self.zone_resets.extend(data)
                        count += 1
            except: pass
        print(f"⚙️ [WORLD] {count} pergaminhos de ritual (Resets) carregados.")

    def populate_world(self):
        """Popula o mundo com logs de DEBUG."""
        mobs_loaded = 0
        items_loaded = 0
        errors = 0
        
        last_mob = None 
        
        for cmd in self.zone_resets:
            try:
                ctype = cmd.get('command')
                
                # M: Carregar Mob
                if ctype == 'M':
                    mob_id = str(cmd.get('mob_vnum'))
                    room_id = str(cmd.get('room_vnum'))
                    
                    target_room = self.get_room(room_id)
                    if not target_room:
                        # print(f"   [DEBUG] Falha Reset M: Sala {room_id} não existe.")
                        errors += 1
                        continue

                    mob = self.create_mob(mob_id)
                    if mob:
                        mob.room = target_room
                        target_room.people.append(mob)
                        last_mob = mob
                        mobs_loaded += 1
                    else:
                        # print(f"   [DEBUG] Falha Reset M: Mob {mob_id} não encontrado.")
                        errors += 1
                
                # O: Carregar Objeto
                elif ctype == 'O':
                    obj_id = str(cmd.get('obj_vnum'))
                    room_id = str(cmd.get('room_vnum'))
                    
                    target_room = self.get_room(room_id)
                    if target_room:
                        item = self.create_item(obj_id)
                        if item:
                            target_room.contents.append(item)
                            items_loaded += 1

                # G: Give (Dar ao Mob)
                elif ctype == 'G':
                    obj_id = str(cmd.get('obj_vnum'))
                    if last_mob:
                        item = self.create_item(obj_id)
                        if item:
                            last_mob.inventory.append(item)
                            items_loaded += 1

                # E: Equip (Equipar Mob)
                elif ctype == 'E':
                    obj_id = str(cmd.get('obj_vnum'))
                    if last_mob:
                        item = self.create_item(obj_id)
                        if item:
                            last_mob.inventory.append(item) # Simplificado
                            items_loaded += 1

            except Exception as e:
                pass

        print(f"📊 [POPULAÇÃO] {mobs_loaded} Mobs e {items_loaded} Itens criados. ({errors} falhas de referência).")

    # --- Factory ---
    def get_room(self, vnum: str) -> Room:
        return self.room_blueprints.get(str(vnum))

    def create_item(self, vnum: str) -> Item:
        proto = self.item_blueprints.get(str(vnum))
        if not proto: return None
        new_item = Item.__new__(Item)
        new_item.__dict__ = proto.__dict__.copy()
        new_item.keywords = list(proto.keywords)
        return new_item

    def create_mob(self, vnum: str) -> Mob:
        proto = self.mob_blueprints.get(str(vnum))
        if not proto: return None
        new_mob = Mob.__new__(Mob)
        new_mob.__dict__ = proto.__dict__.copy()
        new_mob.inventory = []
        new_mob.equipment = {}
        new_mob.keywords = list(proto.keywords)
        return new_mob

    # --- Players ---
    def add_player(self, player):
        if player not in self.active_players:
            self.active_players.append(player)

    def remove_player(self, player):
        if player in self.active_players:
            self.active_players.remove(player)

world = World()