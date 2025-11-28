# AETERNUS - Sistema de Magia

## Estrutura de Feiço
```
{
  "id": "fireball",
  "name": "Fireball",
  "description": "Lança uma bola de fogo",
  "mana_cost": 30,
  "cooldown": 3.0,
  "range": 20,
  "damage": 40,
  "effects": ["burn"],
  "requirements": {
    "intelligence": 15,
    "level": 10
  }
}
```

## Mana
- Pool baseado em Intelligence
- Regenera 5 mana/segundo
- Haste multiplica regeneração

## Spell Schools
- Fire: Damage + Burn
- Ice: Damage + Slow
- Lightning: Damage + Stun
- Healing: Restore HP + Cure

## Resistências
- NPC pode resistir feiços
- Diminui damage em 30-50%
- Podem absorver inteiramente em rare cases
