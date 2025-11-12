from typing import Dict, List, Optional

class Room:
    """
    Um fragmento da realidade.
    Onde o jogador pisa, respira e observa.
    """
    def __init__(self, data: dict):
        # Identidade
        self.vnum: str = str(data.get("vnum", "0"))
        self.name: str = data.get("name", "Vazio Indefinido")
        self.description: str = data.get("description", "Apenas escuridão e silêncio.")
        
        # Geografia (Saídas)
        self.exits: Dict[str, dict] = data.get("exits", {})
        
        # Conteúdo (Quem está aqui?)
        self.contents: List = []  # Itens
        self.people: List = []    # Jogadores/Mobs

    def get_display(self) -> str:
        """
        Retorna a string formatada para ser enviada ao terminal do jogador.
        """
        buffer = []
        
        # 1. Título (Ciano Brilhante)
        buffer.append(f"\033[1;36m{self.name}\033[0m \033[90m[#{self.vnum}]\033[0m")
        
        # 2. Descrição (Branco Suave)
        buffer.append(f"\033[0;37m{self.description}\033[0m")
        
        # 3. Saídas (Verde/Amarelo)
        if self.exits:
            dirs = ", ".join([k.upper() for k in self.exits.keys()])
            buffer.append(f"\033[1;32m[Saídas: {dirs}]\033[0m")
        else:
            buffer.append("\033[1;30m[Não há saídas visíveis]\033[0m")
            
        return "\n".join(buffer)

    def __repr__(self):
        return f"<Room {self.vnum}: {self.name}>"