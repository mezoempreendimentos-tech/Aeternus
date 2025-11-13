class CharacterClass:
    """
    Define o arquétipo de um personagem (Guerreiro, Mago, Novato).
    """
    def __init__(self, data: dict):
        self.vnum = data.get("vnum", "class_unknown")
        self.name = data.get("name", "Desconhecido")
        self.description = data.get("description", "")
        
        self.playable = data.get("playable", False)
        
        # Crescimento
        self.base_hp = int(data.get("base_hp", 100))
        self.hp_per_level = int(data.get("hp_per_level", 10))
        self.mana_per_level = int(data.get("mana_per_level", 5))
        self.stamina_per_level = int(data.get("stamina_per_level", 10))
        
        # Modificadores
        stats = data.get("stat_modifiers", {})
        self.mod_str = float(stats.get("strength", 1.0))
        self.mod_dex = float(stats.get("dexterity", 1.0))
        self.mod_con = float(stats.get("constitution", 1.0))
        self.mod_int = float(stats.get("intelligence", 1.0))
        self.mod_wis = float(stats.get("wisdom", 1.0))
        self.mod_cha = float(stats.get("charisma", 1.0))
        
        # Gear
        self.starting_gear = data.get("starting_gear", [])

    def __repr__(self):
        return f"<Class: {self.name}>"