from typing import Dict, List, Optional

class Room:
    """
    Um fragmento da realidade.
    Onde o jogador pisa, respira e observa.
    """
    
    # A Ordem Sagrada das Direções (Prioridade de Exibição)
    EXIT_ORDER = [
        "north", "northeast", "east", "southeast", 
        "south", "southwest", "west", "northwest", 
        "up", "down"
    ]
    
    # Tradução para exibição bonita
    DIR_NAMES = {
        "north": "Norte", "northeast": "Nordeste", "east": "Leste", "southeast": "Sudeste",
        "south": "Sul", "southwest": "Sudoeste", "west": "Oeste", "northwest": "Noroeste",
        "up": "Cima", "down": "Baixo"
    }

    def __init__(self, data: dict):
        # Identidade
        self.vnum: str = str(data.get("vnum", "0"))
        self.name: str = data.get("name", "Vazio Indefinido")
        self.description: str = data.get("description", "Apenas escuridão e silêncio.")
        
        # Geografia (Saídas)
        self.exits: Dict[str, dict] = data.get("exits", {})
        
        # Conteúdo (Quem está aqui?)
        self.contents: List = []  # Itens (Objetos)
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
        
        # 3. Saídas (Ordenadas e Traduzidas)
        if self.exits:
            # Pega as chaves (direções) que existem nesta sala
            available_exits = list(self.exits.keys())
            
            # Ordena baseado na lista EXIT_ORDER
            available_exits.sort(key=lambda x: self.EXIT_ORDER.index(x) if x in self.EXIT_ORDER else 99)
            
            # Formata para exibição
            display_exits = [self.DIR_NAMES.get(d, d.title()) for d in available_exits]
            dirs_str = ", ".join(display_exits)
            
            buffer.append(f"\033[1;32m[Saídas: {dirs_str}]\033[0m")
        else:
            buffer.append("\033[1;30m[Não há saídas visíveis]\033[0m")

        # 4. Listar Conteúdo (Mobs e Itens)
        
        # Mobs (Pessoas/NPCs)
        if self.people:
            for person in self.people:
                # Verifica se o objeto tem o método get_display (evita crash se for algo estranho)
                if hasattr(person, "get_display"):
                    # Futuramente: não mostrar a si mesmo (if person != looker)
                    # Por enquanto, mostramos o 'display' do mob (ex: "Um guarda está aqui.")
                    # Nota: Jogadores (Connection) não têm get_display ainda, então isso filtra eles.
                    if hasattr(person, "long_desc"): # É um Mob
                         buffer.append(person.get_display())
        
        # Itens (Objetos no chão)
        if self.contents:
            for item in self.contents:
                if hasattr(item, "get_display"):
                    buffer.append(f"\033[0;32m{item.get_display()}\033[0m")
            
        return "\n".join(buffer)

    def __repr__(self):
        return f"<Room {self.vnum}: {self.name}>"