# AETERNUS - Sistema de Crafting

## Estrutura de Receita
```
{
  "id": "iron_sword",
  "name": "Iron Sword",
  "materials": {
    "iron_bar": 3,
    "leather": 1
  },
  "skill_required": "blacksmith",
  "skill_level": 10,
  "time": 30,
  "quality_range": [0.5, 1.5]
}
```

## Qualidade
- Baseada em diferença entre skill e dificuldade
- Afeta damage, durability, valor
- Pode gerar items únicos em high quality

## Skills de Crafting
- Blacksmith: Armas e armaduras
- Alchemy: Poções
- Enchanting: Itens mágicos
- Cooking: Comida

## Durability
- Decresce com uso
- Pode ser reparado (custo)
- Item quebrado = inutilizável
