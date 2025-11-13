from .character import Character
from aeternus.game.world import world

class Player(Character):
    """
    Um avatar controlado por uma alma humana (Connection).
    """
    def __init__(self, name: str):
        super().__init__("player_vnum", name)
        
        self.title = "o Novato"
        self.password = ""       # Futuro: Hash real
        self.connection = None   
        
        # Dados de Persistência Básica
        self.creation_date = 0
        self.last_login = 0

    def get_short_desc(self):
        return f"{self.name} {self.title}"
        
    def __repr__(self):
        return f"<Player: {self.name}>"

    # --- SERIALIZAÇÃO (Salvar) ---
    def to_dict(self) -> dict:
        """Converte o jogador em um dicionário puro para salvar em JSON."""
        return {
            "name": self.name,
            "password": self.password,
            "title": self.title,
            "level": self.level,
            "hp": self.hp,
            "max_hp": self.max_hp,
            # Salvamos apenas o VNUM da sala atual
            "room_vnum": self.room.vnum if self.room else "3001",
            # Salvamos apenas os VNUMs dos itens (simplificação v1)
            "inventory": [item.vnum for item in self.inventory]
        }

    # --- DESERIALIZAÇÃO (Carregar) ---
    def load_from_dict(self, data: dict):
        """Restaura o estado do jogador a partir dos dados salvos."""
        self.password = data.get("password", "")
        self.title = data.get("title", "o Viajante")
        self.level = data.get("level", 1)
        self.hp = data.get("hp", 100)
        self.max_hp = data.get("max_hp", 100)
        
        # Restaurar Inventário
        # O save tem apenas os IDs ["3001", "10"], precisamos recriar os objetos
        saved_inventory = data.get("inventory", [])
        self.inventory = [] # Limpa atual
        
        for item_vnum in saved_inventory:
            item_obj = world.create_item(item_vnum)
            if item_obj:
                self.inventory.append(item_obj)
        
        # Nota: A Sala é tratada no connection.py durante o login
        return data.get("room_vnum", "3001")