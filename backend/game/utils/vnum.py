# backend/game/utils/vnum.py
from typing import Tuple, Union

# Constantes da Arquitetura VNUM
LEGACY_LIMIT = 99999           # Até 5 dígitos é considerado Legado
ID_LIMIT = 99999               # Limite de IDs por zona (5 dígitos)
ZONE_MULTIPLIER = 100000       # Move 5 casas para a esquerda

class VNum:
    """
    Manipulador Estático de Virtual Numbers.
    Gerencia a dualidade entre o sistema Legado (5 dígitos) e o Aeternus (8 dígitos).
    
    Padrão Novo: ZZZXXXXX
    - ZZZ: Zona (0-999)
    - XXXXX: ID Local (0-99999)
    """

    @staticmethod
    def create(zone_id: int, local_id: int) -> int:
        """
        Cria um VNUM Novo (Padrão 8 dígitos).
        Ex: Zone 1, ID 1 -> 100001
        Ex: Zone 12, ID 500 -> 1200500
        """
        if local_id > ID_LIMIT:
            raise ValueError(f"ID Local excede o limite de 5 dígitos ({ID_LIMIT})")
        if zone_id > 999:
            raise ValueError("ID de Zona excede o limite de 3 dígitos (999)")
        
        # Fórmula: (Zone * 100.000) + ID
        return (zone_id * ZONE_MULTIPLIER) + local_id

    @staticmethod
    def parse(vnum: Union[int, str]) -> Tuple[int, int]:
        """
        Decompõe um VNUM em seus componentes (Zone, LocalID).
        Retorna: (zone_id, local_id)
        """
        try:
            val = int(vnum)
        except ValueError:
            return 0, 0 # VNUM Inválido/Erro

        # Se for Legado (<= 99999), assume Zona 0.
        if val <= LEGACY_LIMIT:
            return 0, val

        # Matemática reversa para o Padrão Novo
        zone_id = val // ZONE_MULTIPLIER
        local_id = val % ZONE_MULTIPLIER
        
        return zone_id, local_id

    @staticmethod
    def is_legacy(vnum: int) -> bool:
        """Retorna True se o VNUM pertencer à Era Antiga (<= 99999)."""
        return vnum <= LEGACY_LIMIT

    @staticmethod
    def to_string(vnum: int) -> str:
        """
        Formatação para logs, editores e debug.
        Ex Legado: "LEGACY:15200"
        Ex Novo:   "Z001:00001"
        """
        if VNum.is_legacy(vnum):
            return f"LEGACY:{vnum:05d}"
        
        z, i = VNum.parse(vnum)
        return f"Z{z:03d}:{i:05d}"