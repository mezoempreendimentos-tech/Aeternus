class Item:
    """
    Um objeto inanimado que pode ser pego, usado ou equipado.
    """
    def __init__(self, data: dict):
        self.vnum = str(data.get("vnum", "0"))
        self.name = data.get("name", "Um objeto sem forma")
        self.description = data.get("description", "Algo indescritível.")
        self.keywords = data.get("keywords", [])
        
        # Se keywords vier como string "espada longa", vira lista ["espada", "longa"]
        if isinstance(self.keywords, str):
            self.keywords = self.keywords.split()

        # Propriedades Físicas (Padrões)
        self.type = data.get("type", "trash")
        self.weight = float(data.get("weight", 1.0))
        self.cost = int(data.get("cost", 0))
        
        # Tags do Codex (Futuro)
        self.tags = set()

    def get_display(self):
        """Como o item aparece no chão."""
        return f"{self.description}"

    def get_short_desc(self):
        """Como o item aparece no inventário (ex: uma espada longa)."""
        return self.name

    def __repr__(self):
        return f"<Item {self.vnum}: {self.name}>"