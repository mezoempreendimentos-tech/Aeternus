# Configurações de Jogo AETERNUS

GAME_CONSTANTS = {
    "MAX_LEVEL": 50,
    "BASE_HEALTH": 100,
    "BASE_MANA": 50,
    "MANA_REGEN_RATE": 5,  # por segundo
    "COMBAT_TICK": 0.5,    # segundos
    "NPC_DECISION_INTERVAL": (10, 30),  # random entre isso
    "WORLD_TICK": 1.0,     # tick do mundo
    "SESSION_TIMEOUT": 1800,  # 30 minutos inativo
}

CLASS_STATS = {
    "warrior": {
        "strength": 12,
        "dexterity": 10,
        "intelligence": 8,
        "wisdom": 10,
        "constitution": 13,
    },
    "mage": {
        "strength": 8,
        "dexterity": 10,
        "intelligence": 14,
        "wisdom": 12,
        "constitution": 9,
    },
    "rogue": {
        "strength": 10,
        "dexterity": 14,
        "intelligence": 10,
        "wisdom": 11,
        "constitution": 10,
    },
    "priest": {
        "strength": 10,
        "dexterity": 11,
        "intelligence": 12,
        "wisdom": 14,
        "constitution": 11,
    },
}

RACE_BONUSES = {
    "human": {"all": 0},
    "elf": {"dexterity": 2, "intelligence": 1},
    "dwarf": {"constitution": 2, "strength": 1},
    "halfling": {"dexterity": 3, "strength": -1},
}
