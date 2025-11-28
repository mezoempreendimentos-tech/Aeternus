# AETERNUS - Comportamento de NPCs com IA

## Arquétipos de NPC
1. **Warrior**: Ataca diretamente, comportamento agressivo
2. **Merchant**: Negocia, avesso a combate
3. **Mage**: Usa feiços, mantém distância
4. **Rogue**: Emboscadas, fugas rápidas
5. **Priest**: Heal allies, buffs

## Contexto para Ollama
```
NPC: "Goblin Warrior"
Personality: Aggressive, territorial
Memory: [last 5 interactions]
Current State: Patrolling
Nearby: 1 player approaching
Instruction: Decide next action
```

## Decisões Típicas
- Attack: Enemy nearby
- Patrol: Routine movement
- Dialogue: Player interaction
- Flee: Low HP
- Heal: Ally damaged

## Fallback Behaviors
Se Ollama falhar:
- Comportamento baseado em regras
- Estado anterior + noise
- Sempre garantido uma ação válida

## Emotes Periódicos
A cada 30-60s, NPC faz emote (via Ollama background)
- "Goblin yawns"
- "Merchant counts coins"
- "Mage mutters arcane words"
