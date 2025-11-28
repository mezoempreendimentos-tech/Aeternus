# AETERNUS - Sistema de Habilidades

## Estrutura de Skill
```
{
  "id": "slash",
  "name": "Slash",
  "description": "Um ataque cortante básico",
  "type": "melee",
  "damage_multiplier": 1.0,
  "cooldown": 1.5,
  "mana_cost": 0,
  "requirements": {
    "strength": 10,
    "level": 1
  },
  "effects": []
}
```

## Categorias
- Melee: Ataques próximos
- Ranged: Ataques à distância
- Magic: Feiços
- Utility: Habilidades especiais

## Cooldown
- Tempo mínimo entre usos
- Reduced by haste effects
- Zeroed on certain conditions
