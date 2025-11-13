from .character import Character

class Mob(Character):
    """
    Uma criatura movida pela vontade do sistema (IA).
    """
    def __init__(self, data: dict):
        vnum = str(data.get("vnum", "0"))
        name = data.get("name", "Uma criatura sem nome")
        super().__init__(vnum, name)
        
        # Mapeamento corrigido conforme o YAML gerado:
        # name: "pacificador"
        # description: "Um Pacificador está aqui..." (Room Message)
        # long_desc: "Ele parece forte..." (Detailed Look)
        
        self.description = data.get("description", f"{self.name} está aqui.")
        self.long_desc = data.get("long_desc", "")
        
        self.level = int(data.get("level", 1))
        self.max_hp = int(data.get("max_hp", 100))
        self.hp = self.max_hp
        
        self.keywords = data.get("keywords", [])
        if isinstance(self.keywords, str):
            self.keywords = self.keywords.split()

    def get_display(self):
        """
        Retorna o texto para mostrar na sala.
        Deve ser a frase completa (ex: 'Um Pacificador está aqui.').
        """
        return f"\033[1;33m{self.description.strip()}\033[0m"

    def get_detailed_look(self):
        """Retorna o texto quando alguém dá 'look mob'."""
        return self.long_desc

    def __repr__(self):
        return f"<Mob {self.vnum}: {self.name}>"