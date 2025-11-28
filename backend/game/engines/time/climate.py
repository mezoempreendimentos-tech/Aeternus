# backend/game/engines/time/climate.py
from typing import Dict

# Tipos de Clima de Zona (Adicionar nas Flags da Zone/Room)
CLIMATE_TEMPERATE = "TEMPERATE"  # Segue as estações normais
CLIMATE_ARCTIC = "ARCTIC"        # Sempre frio
CLIMATE_DESERT = "DESERT"        # Varia entre quente e infernal
CLIMATE_TROPICAL = "TROPICAL"    # Chuvoso ou Seco, sempre quente
CLIMATE_UNDERGROUND = "UNDERGROUND" # Constante

def get_zone_weather(season: str, climate_type: str) -> Dict[str, str]:
    """
    Retorna o estado do tempo baseado na matriz Estação x Clima.
    Retorna dict com descrição e flags de efeito.
    """
    
    # 1. Zonas Subterrâneas (Ignoram o sol)
    if climate_type == CLIMATE_UNDERGROUND:
        return {
            "desc": "O ar é estagnado e a temperatura constante.",
            "temp": "neutral",
            "precip": "none"
        }

    # 2. Zonas Árticas (O 'Verão' é apenas menos mortal)
    if climate_type == CLIMATE_ARCTIC:
        if season in ["Zênite", "Abrasamento"]:
            return {"desc": "Um vento gélido sopra, mas o gelo derrete levemente.", "temp": "cold", "precip": "none"}
        else:
            return {"desc": "Uma nevasca eterna uiva, congelando a medula.", "temp": "freezing", "precip": "snow"}

    # 3. Zonas Temperadas (Padrão)
    if climate_type == CLIMATE_TEMPERATE:
        mapping = {
            "Renascimento": {"desc": "Brisas frescas carregam o cheiro de terra molhada.", "temp": "cool", "precip": "rain"},
            "Ascensão":     {"desc": "O sol aquece a terra agradavelmente.", "temp": "warm", "precip": "none"},
            "Zênite":       {"desc": "O calor faz o ar tremeluzir.", "temp": "hot", "precip": "none"},
            "Abrasamento":  {"desc": "A vegetação seca estala sob o sol impiedoso.", "temp": "hot", "precip": "none"},
            "Declínio":     {"desc": "Folhas caem sob um céu cinzento.", "temp": "cool", "precip": "wind"},
            "Penumbra":     {"desc": "Chuvas frias anunciam o fim do ano.", "temp": "cold", "precip": "rain"},
            "Torpor":       {"desc": "Geada cobre o solo endurecido.", "temp": "freezing", "precip": "snow"}
        }
        return mapping.get(season, mapping["Renascimento"])

    # Fallback
    return {"desc": "O clima é indecifrável.", "temp": "neutral", "precip": "none"}