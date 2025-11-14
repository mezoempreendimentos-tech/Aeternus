import os
import yaml
from pathlib import Path
from aeternus.game.objects.room import Room
from aeternus.game.objects.item import Item
from aeternus.game.objects.mob import Mob
from aeternus.game.objects.character_class import CharacterClass
from aeternus.core.config import settings

# --- CONSTANTES DO TEMPO ---
SEASONS = {
    0: ("Primoris", "O Despertar", "O ar cheira a flores e vida nova."),
    1: ("Aestas", "O Ardor", "O sol castiga a terra com ondas de calor."),
    2: ("Virens", "O Viço", "A vegetação cresce de forma selvagem e agressiva."),
    3: ("Messis", "A Colheita", "Os campos estão dourados e o clima é ameno."),
    4: ("Ventus", "A Ventania", "Ventos uivantes varrem as folhas e agitam os mares."),
    5: ("Caducus", "O Ocaso", "Tudo apodrece. O cheiro de terra molhada e fim permeia o ar."),
    6: ("Hiems", "O Inverno", "O mundo congela sob um manto de silêncio branco.")
}

# 13 Meses de 28 dias. Distribuição das estações (aprox 2 meses cada)
MONTH_TO_SEASON = {
    1: 0, 2: 0,  # Primoris
    3: 1, 4: 1,  # Aestas
    5: 2, 6: 2,  # Virens
    7: 3, 8: 3,  # Messis
    9: 4, 10: 4, # Ventus
    11: 5, 12: 5,# Caducus
    13: 6        # Hiems (O mês longo e escuro)
}

class World:
    def __init__(self):
        self.room_blueprints: dict[str, Room] = {}
        self.item_blueprints: dict[str, Item] = {}
        self.mob_blueprints: dict[str, Mob] = {}
        self.class_blueprints: dict[str, CharacterClass] = {}
        self.zone_resets: list = []
        self.active_players: list = [] 
        
        # --- CRONOS AETERNUS ---
        self.hour = 6   # 0-23
        self.day = 1    # 1-28
        self.month = 1  # 1-13
        self.year = 1   # Era 1

    @property
    def current_season(self):
        """Retorna ID, Nome, Subtitulo, Descrição da estação atual."""
        sid = MONTH_TO_SEASON.get(self.month, 0)
        return {"id": sid, "name": SEASONS[sid][0], "title": SEASONS[sid][1], "desc": SEASONS[sid][2]}

    def is_night(self):
        return self.hour >= 22 or self.hour < 5

    def is_day(self):
        return not self.is_night()

    def advance_time(self):
        """
        Avança 1 hora no mundo.
        Chamado a cada minuto real pelo GameLoop.
        """
        self.hour += 1
        msgs = []

        # Eventos de Hora (Sol/Lua)
        if self.hour == 6: msgs.append("\033[1;33mO sol nasce, revelando as cores de " + self.current_season['name'] + ".\033[0m")
        elif self.hour == 12: msgs.append("\033[1;33mO sol atinge o zênite.\033[0m")
        elif self.hour == 18: msgs.append("\033[0;31mO sol se põe no horizonte sangrento.\033[0m")
        elif self.hour == 0: msgs.append("\033[1;34mA lua reina absoluta no céu noturno.\033[0m")

        # Virada do Dia
        if self.hour >= 24:
            self.hour = 0
            self.day += 1
            msgs.append("Um novo dia começa.")
            
            # Virada do Mês
            if self.day > 28:
                self.day = 1
                self.month += 1
                
                # Virada da Estação (Talvez)
                season = self.current_season
                msgs.append(f"\n\033[1;36m=== A ESTAÇÃO MUDOU PARA {season['name'].upper()} ({season['title']}) ===\033[0m")
                msgs.append(f"\033[0;36m{season['desc']}\033[0m\n")

                # Virada do Ano
                if self.month > 13:
                    self.month = 1
                    self.year += 1
                    msgs.append(f"\n\033[1;35mFELIZ ANO NOVO! Iniciamos o Ano {self.year} da Era Aeternus.\033[0m\n")

        if msgs:
            print(f"⏰ [TIME] {self.hour}:00 - {msgs[0]}")
            return "\n".join(msgs)
        return None

    # ... (O RESTANTE DO ARQUIVO PERMANECE IGUAL: load_assets, populate, factory...) ...
    # COPIE AS FUNÇÕES DE LOAD/POPULATE DO ARQUIVO ANTERIOR PARA AQUI
    
    def load_assets(self):
        print("🌍 [WORLD] Iniciando a Gênese...")
        self._load_generic("rooms.yaml", Room, self.room_blueprints, "Salas")
        self._load_generic("items.yaml", Item, self.item_blueprints, "Itens")
        self._load_generic("mobs.yaml", Mob, self.mob_blueprints, "Criaturas")
        self._load_classes()
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
                        vnum = str(entry.get('vnum'))
                        obj = class_ref(entry)
                        target_dict[vnum] = obj
                        count += 1
            except: pass
        print(f"📦 [WORLD] {count} {label} carregados.")

    def _load_classes(self):
        search_path = settings.BLUEPRINTS_DIR / "classes"
        search_path.mkdir(parents=True, exist_ok=True)
        files = list(search_path.rglob("*.yaml"))
        count = 0
        for yaml_file in files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if not data: continue
                    if isinstance(data, dict): data = [data]
                    for entry in data:
                        cls = CharacterClass(entry)
                        self.class_blueprints[cls.vnum] = cls
                        count += 1
            except: pass
        print(f"📚 [WORLD] {count} classes acadêmicas registradas.")

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
        mobs_loaded = 0
        last_mob = None 
        for cmd in self.zone_resets:
            try:
                ctype = cmd.get('command')
                if ctype == 'M':
                    mob_id = str(cmd.get('mob_vnum'))
                    room_id = str(cmd.get('room_vnum'))
                    limit = int(cmd.get('limit', 999))
                    target_room = self.get_room(room_id)
                    if target_room:
                        count_in_room = sum(1 for m in target_room.people if getattr(m, 'vnum', '') == mob_id)
                        if count_in_room >= limit: continue
                        mob = self.create_mob(mob_id)
                        if mob:
                            mob.room = target_room
                            target_room.people.append(mob)
                            last_mob = mob
                            mobs_loaded += 1
                elif ctype == 'O':
                    obj_id = str(cmd.get('obj_vnum'))
                    room_id = str(cmd.get('room_vnum'))
                    target_room = self.get_room(room_id)
                    if target_room:
                        item = self.create_item(obj_id)
                        if item: target_room.contents.append(item)
                elif ctype == 'G':
                    obj_id = str(cmd.get('obj_vnum'))
                    if last_mob:
                        item = self.create_item(obj_id)
                        if item: last_mob.inventory.append(item)
                elif ctype == 'E':
                    obj_id = str(cmd.get('obj_vnum'))
                    if last_mob:
                        item = self.create_item(obj_id)
                        if item: last_mob.inventory.append(item)
            except: pass

    def get_room(self, vnum: str) -> Room: return self.room_blueprints.get(str(vnum))
    def get_class(self, vnum: str) -> CharacterClass: return self.class_blueprints.get(vnum)
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
    def add_player(self, player):
        if player not in self.active_players: self.active_players.append(player)
    def remove_player(self, player):
        if player in self.active_players: self.active_players.remove(player)

world = World()