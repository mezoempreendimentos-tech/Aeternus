from .character import Character
from aeternus.game.world import world

class Player(Character):
    """
    Um avatar controlado por uma alma humana (Connection).
    """
    def __init__(self, name: str):
        super().__init__("player_vnum", name)
        
        self.title = "o Novato"
        self.password = ""       
        self.connection = None   
        
        # Persistência
        self.creation_date = 0
        self.last_login = 0
        
        # Variável temporária para segurar o ID da sala ao carregar
        self.saved_room_vnum = None 

    def get_short_desc(self):
        return f"{self.name} {self.title}"
        
    def __repr__(self):
        return f"<Player: {self.name}>"

    # --- SERIALIZAÇÃO (Salvar) ---
    def to_dict(self) -> dict:
        """Salva o estado atual."""
        # Se o jogador está numa sala válida, salva o VNUM dela.
        # Se não, tenta usar o último salvo ou fallback para a praça.
        current_room_id = "3001"
        if self.room:
            current_room_id = self.room.vnum
        elif self.saved_room_vnum:
            current_room_id = self.saved_room_vnum

        return {
            "name": self.name,
            "password": self.password,
            "title": self.title,
            "level": self.level,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "room_vnum": current_room_id, # <--- Salva onde parou
            "inventory": [item.vnum for item in self.inventory]
        }

    # --- DESERIALIZAÇÃO (Carregar) ---
    def load_from_dict(self, data: dict):
        """Restaura o estado."""
        self.password = data.get("password", "")
        self.title = data.get("title", "o Viajante")
        self.level = data.get("level", 1)
        self.hp = data.get("hp", 100)
        self.max_hp = data.get("max_hp", 100)
        
        # Carrega o ID da sala para memória temporária
        # (A conexão vai decidir se esse ID é válido ou não)
        self.saved_room_vnum = data.get("room_vnum") 
        
        # Restaurar Inventário
        saved_inventory = data.get("inventory", [])
        self.inventory = [] 
        
        for item_vnum in saved_inventory:
            item_obj = world.create_item(item_vnum)
            if item_obj:
                self.inventory.append(item_obj)