import uuid
from typing import List, Dict, Any

class Entity:
    """
    A raiz de toda a existência no Aeternus.
    Mobs, Itens e Salas herdam desta essência.
    
    Respeita o CODEX 1:
    - vnum: O Molde (De onde eu vim? ex: 'sword_steel')
    - uuid: A Alma (Quem sou eu? ex: 'sword_steel_#99281')
    """
    
    def __init__(self, vnum: str, name: str):
        self.vnum = vnum
        # O UUID garante que duas espadas iguais sejam objetos distintos no mundo
        self.uuid = uuid.uuid4()
        
        self.name = name
        self.description = "Uma forma nebulosa sem definição clara."
        
        # Tags (CODEX TAGNATURA): Substituem os bitvectors (IS_EVIL, IS_MAGIC)
        self.tags: set[str] = set()
        
        # Scripts anexados (Triggers)
        self.scripts: List[str] = []

    def has_tag(self, tag: str) -> bool:
        """Verifica se a entidade possui uma característica semântica."""
        return tag in self.tags

    def __repr__(self):
        return f"<{self.__class__.__name__} | {self.name} ({self.vnum})>"