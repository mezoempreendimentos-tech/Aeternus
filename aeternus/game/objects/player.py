from .character import Character
from aeternus.game.world import world

class Player(Character):
    def __init__(self, name: str):
        super().__init__("player_vnum", name)
        
        self.title = "o Novato"
        self.password = ""       
        self.connection = None   
        self.creation_date = 0
        self.last_login = 0
        self.saved_room_vnum = None 

    def get_short_desc(self):
        return f"{self.name} {self.title}"
        
    def __repr__(self):
        return f"<Player: {self.name}>"

    # --- SERIALIZAÇÃO ---
    def to_dict(self) -> dict:
        current_room_id = "3001"
        if self.room: current_room_id = self.room.vnum
        elif self.saved_room_vnum: current_room_id = self.saved_room_vnum

        return {
            "name": self.name,
            "password": self.password,
            "title": self.title,
            "level": self.level,
            "hp": self.hp, "max_hp": self.max_hp,
            "mana": self.mana, "max_mana": self.max_mana,       # Salvando Mana
            "stamina": self.stamina, "max_stamina": self.max_stamina, # Salvando Stamina
            "room_vnum": current_room_id,
            "inventory": [item.vnum for item in self.inventory],
            "spells_known": list(self.spells_known) # <--- Salva Magias
        }

    # --- DESERIALIZAÇÃO ---
    def load_from_dict(self, data: dict):
        self.password = data.get("password", "")
        self.title = data.get("title", "o Viajante")
        self.level = data.get("level", 1)
        self.hp = data.get("hp", 100); self.max_hp = data.get("max_hp", 100)
        self.mana = data.get("mana", 100); self.max_mana = data.get("max_mana", 100)
        self.stamina = data.get("stamina", 100); self.max_stamina = data.get("max_stamina", 100)
        
        self.saved_room_vnum = data.get("room_vnum") 
        
        # Restaura Magias
        self.spells_known = set(data.get("spells_known", []))

        # Restaura Inventário
        saved_inventory = data.get("inventory", [])
        self.inventory = [] 
        for item_vnum in saved_inventory:
            item_obj = world.create_item(item_vnum)
            if item_obj: self.inventory.append(item_obj)