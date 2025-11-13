from .entity import Entity

class Character(Entity):
    """
    A essência de qualquer ser vivo no Aeternus.
    Jogadores e Mobs herdam daqui.
    Aqui reside a carne (HP), a posse (Inventário) e os Atributos.
    """
    def __init__(self, vnum: str, name: str):
        super().__init__(vnum, name)
        
        # --- A MATÉRIA (Vitals) ---
        self.max_hp = 100
        self.hp = 100
        self.max_mana = 100
        self.mana = 100
        self.max_stamina = 100
        self.stamina = 100
        
        self.level = 1
        
        # --- A CLASSE E ATRIBUTOS (Stats) ---
        self.class_vnum = "class_novice" # Padrão para todos
        
        self.strength = 10
        self.dexterity = 10
        self.constitution = 10
        self.intelligence = 10
        self.wisdom = 10
        self.charisma = 10
        
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