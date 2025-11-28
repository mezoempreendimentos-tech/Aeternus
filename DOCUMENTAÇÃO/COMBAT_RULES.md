# AETERNUS - Regras de Combate

## Fluxo de Combate
1. Ambos rolam iniciativa (d20 + DEX modifier)
2. Ordem de turnos estabelecida
3. Cada turno: atacante escolhe ação
4. Defender reage automaticamente ou escolhe ação
5. Loop até morte de um

## Cálculo de Dano
```
base_damage = weapon_damage + (strength * 0.5)
modified_damage = base_damage * skill_multiplier
total_damage = modified_damage - (enemy_armor * 0.2)
final_damage = max(1, total_damage)
```

## Efeitos de Combate
- Bleed: -5 HP/tick por 5 ticks
- Stun: Miss próximo turno
- Haste: +20% speed
- Blind: -30% accuracy

## Morte
- HP atinge 0
- Respawn em última cidade
- Perda de 10% de XP não earned
- Dropar 50% do inventory
