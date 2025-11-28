# AETERNUS - Mapa do Mundo

## Estrutura de Áreas
```
The Shattered Isles
├── Starter Zone (Level 1-10)
│   ├── Village Square
│   ├── Training Grounds
│   └── Goblin Caves
├── Forest Region (Level 10-20)
│   ├── Dark Woods
│   ├── Druid Grove
│   └── Bandit Camp
└── Dungeons
    ├── Crystal Cavern (Level 15-25)
    ├── Haunted Manor (Level 25-35)
    └── Dragon's Lair (Level 45-50)
```

## Room Template
```
{
  "id": "village_square",
  "title": "Village Square",
  "description": "A bustling plaza with merchants and adventurers",
  "area": "starter_zone",
  "exits": {
    "north": "training_grounds",
    "south": "tavern",
    "east": "market"
  },
  "spawns": [
    {"npc_id": "merchant", "count": 2, "respawn_time": 300}
  ]
}
```

## Conectividade
- Rooms formam grafo conectado
- Alguns exits requerem password/key
- Boss rooms isoladas
