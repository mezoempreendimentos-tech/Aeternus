# backend/game/engines/time/calendar.py
from dataclasses import dataclass

# Constantes de Tempo
REAL_SECONDS_PER_GAME_DAY = 48 * 60  # 2880 segundos
GAME_SECONDS_PER_DAY = 86400
TIME_MULTIPLIER = 30  # 1 seg real = 30 segs jogo

# Definição do Calendário
MONTHS_PER_YEAR = 13
DAYS_PER_MONTH = 28
HOURS_PER_DAY = 24

# Nomes dos 13 Meses
MONTH_NAMES = [
    "Abertura dos Portões", "O Degelo", "Sementeira", "Vigília do Sol",
    "Fogo Alto", "A Queimada", "A Coroa Dourada", "O Primeiro Vento",
    "Colheita de Sangue", "Folha Seca", "A Névoa", "Gelo Negro", "O Silêncio"
]

# As 7 Estações Globais
SEASONS = [
    "Renascimento",   # Início da Primavera
    "Ascensão",       # Primavera Tardia
    "Zênite",         # Verão
    "Abrasamento",    # Verão Tardio/Seca
    "Declínio",       # Outono
    "Penumbra",       # Outono Tardio
    "Torpor"          # Inverno
]

# Mapeamento: Qual estação ocorre em qual mês? (Índices 0-12)
# Distribuindo 7 estações em 13 meses
MONTH_TO_SEASON = {
    0: "Torpor",        # Abertura (Ainda frio)
    1: "Renascimento",  # Degelo
    2: "Renascimento",  # Sementeira
    3: "Ascensão",      # Vigília
    4: "Zênite",        # Fogo Alto
    5: "Abrasamento",   # Queimada
    6: "Abrasamento",   # Coroa
    7: "Declínio",      # Primeiro Vento
    8: "Declínio",      # Colheita
    9: "Penumbra",      # Folha Seca
    10: "Penumbra",     # Névoa
    11: "Torpor",       # Gelo Negro
    12: "Torpor"        # O Silêncio
}

@dataclass
class GameDate:
    year: int
    month: int  # 1-13
    day: int    # 1-28
    hour: int   # 0-23
    minute: int # 0-59
    
    @property
    def season_name(self) -> str:
        # Ajusta para índice 0-12
        return MONTH_TO_SEASON.get(self.month - 1, "Desconhecido")
        
    def __str__(self):
        m_name = MONTH_NAMES[self.month - 1] if 0 < self.month <= 13 else "???"
        return f"{self.day} de {m_name}, Ano {self.year} ({self.hour:02d}:{self.minute:02d})"