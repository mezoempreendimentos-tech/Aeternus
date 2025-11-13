from .entity import Entity

class Character(Entity):
    """
    A essência de qualquer ser vivo no Aeternus.
    Jogadores e Mobs herdam daqui.
    Aqui reside a carne (HP) e a posse (Inventário).
    """
    def __init__(self, vnum: str, name: str):
        super().__init__(vnum, name)
        
        # --- A MATÉRIA ---
        self.max_hp = 100
        self.hp = 100
        self.level = 1
        
        # --- A POSSE (O Inventário Universal) ---
        self.inventory = []      # Itens na mochila
        self.equipment = {}      # Itens no corpo (slot.head, etc)
        
        # --- O ESPAÇO ---
        self.room = None         # Onde estou?

    def get_short_desc(self):
        return self.name

    def get_display(self):
        """Como apareço para os outros."""
        return f"{self.name} está aqui."