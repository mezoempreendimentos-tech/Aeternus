from .character import Character

class Mob(Character):
    """
    Uma criatura movida pela vontade do sistema (IA).
    """
    def __init__(self, data: dict):
        # Inicia a base (Character -> Entity)
        vnum = str(data.get("vnum", "0"))
        name = data.get("name", "Uma criatura sem nome")
        super().__init__(vnum, name)
        
        # Dados específicos de Mob
        self.short_desc = data.get("short_desc", self.name)
        self.long_desc = data.get("long_desc", f"{self.name} está aqui.")
        self.description = data.get("description", "")
        
        # Stats vindos do YAML
        self.level = int(data.get("level", 1))
        self.max_hp = int(data.get("max_hp", 100))
        self.hp = self.max_hp
        
        self.keywords = data.get("keywords", [])
        if isinstance(self.keywords, str):
            self.keywords = self.keywords.split()

    def get_display(self):
        """Sobrescreve o display padrão para usar a long_desc amarela."""
        return f"\033[1;33m{self.long_desc.strip()}\033[0m"

    def __repr__(self):
        return f"<Mob {self.vnum}: {self.name}>"