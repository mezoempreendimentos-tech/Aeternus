# Guia de Organização de Arquivos para Desenvolvimento do MUD

## ⚠️ REGRA OURO ANTES DE CRIAR QUALQUER ARQUIVO

**ANTES DE CRIAR UM NOVO ARQUIVO:**
1. Procure em `backend/game/engines/` - existe um motor para isso?
2. Procure em `backend/models/` - existe um modelo para isso?
3. Procure em `backend/db/` - existe uma query para isso?
4. Se não existe → ENTÃO pode criar

**NÃO INVENTE PASTAS NOVAS.** Se alguma coisa não cabe perfeitamente, é sinal que deveria estar em um `__init__.py` existente ou em `utils/`.

---

## Matriz de Decisão: Arquivo X vai na Pasta Z

### Se o arquivo trata de...

#### 🎮 **Lógica de Jogo Específica** (Combate, Magia, Skills, etc)

| O que é | Vai em | Padrão |
|---------|--------|--------|
| Classe que orquestra motor | `backend/game/engines/[motor]/[motor].py` | `class CombatEngine` |
| Cálculos puros (sem I/O) | `backend/game/engines/[motor]/[submodulo].py` | `damage_calc.py`, `mana_system.py` |
| Interface com BD/Cache | `backend/game/engines/[motor]/db_interface.py` | Únicas queries específicas do motor |
| Constantes do motor | `backend/config/balance.py` | `COMBAT_DAMAGE_MULTIPLIER = 1.2` |
| Testes do motor | `tests/engines/[motor]/test_[submodulo].py` | Segue estrutura do motor |

**Exemplos:**
- ✅ Arquivo com fórmula de dano → `backend/game/engines/combat/damage_calc.py`
- ✅ Arquivo com cálculo de mana → `backend/game/engines/magic/mana_system.py`
- ✅ Arquivo com cooldown → `backend/game/engines/skills/cooldowns.py`
- ❌ Não criar `backend/game/formulas.py` (espalha lógica)
- ❌ Não criar `backend/game/calculations/` (já existe estrutura melhor)

---

#### 📊 **Modelos de Dados do Jogo** (Classes que representam conceitos)

| O que é | Vai em | Padrão |
|---------|--------|--------|
| Classe Python de Jogador | `backend/models/player.py` | `class Player` |
| Classe Python de NPC | `backend/models/npc.py` | `class NPC` |
| Classe Python de Item | `backend/models/item.py` | `class Item` |
| Classe Python de Sala | `backend/models/room.py` | `class Room` |
| Classe de Combate | `backend/models/combat.py` | `class CombatSession` |
| Classe de Efeito | `backend/models/effect.py` | `class GameEffect` |

**Exemplos:**
- ✅ Definição de estrutura de Player → `backend/models/player.py`
- ✅ Definição de estrutura de Item → `backend/models/item.py`
- ❌ Não criar `backend/game/player_model.py` (já existe `models/player.py`)
- ❌ Não criar `backend/entities/player.py` (já existe estrutura em `models/`)

---

#### 💾 **Banco de Dados e ORM** (Persistência em PostgreSQL)

| O que é | Vai em | Padrão |
|---------|--------|--------|
| Modelo ORM SQLAlchemy | `backend/db/models.py` | `class PlayerORM(Base)` |
| Queries genéricas | `backend/db/queries.py` | `async def get_player(id)` |
| Queries específicas de motor | `backend/game/engines/[motor]/db_interface.py` | Motor acessa DB por aqui |
| Configuração de DB | `backend/db/base.py` | `engine`, `SessionLocal`, `Base` |
| Migrations | `backend/db/migrations/versions/` | Alembic gerado |

**Exemplos:**
- ✅ Query de buscar player → `backend/db/queries.py::get_player()`
- ✅ Queries de combate → `backend/game/engines/combat/db_interface.py` (isoladas no motor)
- ❌ Não criar `backend/queries_combat.py` (perde modularidade)
- ❌ Não criar `backend/game/engines/combat/queries.py` (use `db_interface.py` padrão)

---

#### 🔴 **Cache e Estado Rápido** (Redis, sessões em memória)

| O que é | Vai em | Padrão |
|---------|--------|--------|
| Client Redis | `backend/cache/redis_client.py` | `class RedisClient` |
| Cache de combate | `backend/cache/combat_cache.py` | `set_combat_state()` |
| Cache de player | `backend/cache/player_cache.py` | `get_player_session()` |
| Pub/Sub Redis | `backend/cache/pubsub.py` | Canais de comunicação |
| Estado em memória | `backend/game/state/game_state.py` | `class GameState` |

**Exemplos:**
- ✅ Função para cachear combate → `backend/cache/combat_cache.py`
- ✅ Estado global de jogo → `backend/game/state/game_state.py`
- ❌ Não criar `backend/game/engines/combat/cache.py` (use `backend/cache/combat_cache.py`)
- ❌ Não criar `backend/redis_helpers.py` (especifique melhor em `cache/`)

---

#### 🧠 **Inteligência Artificial e IA de NPCs**

| O que é | Vai em | Padrão |
|---------|--------|--------|
| Cliente Ollama genérico | `backend/ai/ollama_service.py` | `class OllamaService` |
| Prompts estruturados | `backend/ai/prompts.py` | `def get_npc_dialogue_prompt()` |
| Embeddings/contexto | `backend/ai/embeddings.py` | `def embed_context()` |
| Orquestrador de IA | `backend/game/engines/ai/ai.py` | `class AIEngine` |
| Comportamentos NPC | `backend/game/engines/ai/npc_behavior.py` | Decisões baseadas em contexto |
| Diálogos IA | `backend/game/engines/ai/dialogue.py` | Geração de respostas |
| Memória de NPC | `backend/game/engines/ai/memory.py` | Histórico, contexto persistente |
| Rules engine (fallback) | `backend/game/engines/ai/rules_engine.py` | Comportamento sem IA |

**Exemplos:**
- ✅ Wrapper do Ollama → `backend/ai/ollama_service.py`
- ✅ Lógica de NPC reagir → `backend/game/engines/ai/npc_behavior.py`
- ✅ Diálogos do NPC → `backend/game/engines/ai/dialogue.py`
- ❌ Não criar `backend/game/engines/dialogue/` (IA é um motor, diálogos são parte dela)
- ❌ Não criar `backend/ai/npc_behavior.py` (vai em `engines/ai/`)

---

#### 🎪 **Handlers e Orquestração** (Recebem eventos, rotem para motors)

| O que é | Vai em | Padrão |
|---------|--------|--------|
| Parser de comandos | `backend/handlers/command_handler.py` | `class CommandHandler` |
| Eventos WebSocket | `backend/handlers/websocket_handler.py` | `@app.websocket()` |
| Emissor de eventos | `backend/handlers/event_emitter.py` | `class EventEmitter` |

**Exemplos:**
- ✅ Rotear "attack" para combat engine → `backend/handlers/command_handler.py`
- ✅ Nova conexão WebSocket → `backend/handlers/websocket_handler.py`
- ❌ Não criar lógica de combate aqui (vai em `engines/combat/`)
- ❌ Não criar cálculos de dano aqui (vai em `engines/combat/damage_calc.py`)

**Regra:** Handlers NÃO têm lógica complexa. Apenas roteia.

---

#### ⚙️ **APIs e Endpoints**

| O que é | Vai em | Padrão |
|---------|--------|--------|
| Rotas FastAPI | `backend/api/routes.py` | `@app.get()`, `@app.post()` |
| Endpoint WebSocket | `backend/api/websocket.py` | `@app.websocket()` |
| Health checks | `backend/api/health.py` | `@app.get("/health")` |

**Exemplos:**
- ✅ Rota POST para criar personagem → `backend/api/routes.py`
- ✅ Endpoint WebSocket → `backend/api/websocket.py`
- ❌ Não criar handlers de comandos aqui (vai em `handlers/command_handler.py`)
- ❌ Não colocar lógica de jogo aqui (vai em `engines/`)

---

#### 📋 **Configurações e Constantes**

| O que é | Vai em | Padrão |
|---------|--------|--------|
| Constantes de jogo | `backend/config/game_config.py` | `MAX_LEVEL = 50` |
| Balanceamento | `backend/config/balance.py` | `COMBAT_DAMAGE_MULTIPLIER` |
| Configuração de servidor | `backend/config/server_config.py` | `PORT`, `DATABASE_URL` |
| Constantes globais | `backend/config/constants.py` | Enums, valores fixos |

**Exemplos:**
- ✅ Dano base do warrior → `backend/config/balance.py::WARRIOR_BASE_DAMAGE`
- ✅ Nível máximo → `backend/config/game_config.py::MAX_LEVEL`
- ❌ Não criar `backend/config/combat_config.py` (use `balance.py`)
- ❌ Não hardcode em `engine` (busca em `config/`)

---

#### 🌍 **Dados do Mundo** (Templates, blueprints)

| O que é | Vai em | Padrão |
|---------|--------|--------|
| Gerenciador do mundo | `backend/game/world/world_manager.py` | `class WorldManager` |
| Templates de room | `backend/game/world/room_templates.py` | `ROOM_TEMPLATES = {...}` |
| Templates de NPC | `backend/game/world/npc_templates.py` | `NPC_TEMPLATES = {...}` |
| Templates de item | `backend/game/world/item_templates.py` | `ITEM_TEMPLATES = {...}` |
| Definições de áreas | `backend/game/world/area.py` | `class Area` |

**Ou em JSON (dados puros):**
| O que é | Vai em | Padrão |
|---------|--------|--------|
| Definições de classe | `data/classes.json` | Sem lógica, apenas dados |
| Definições de raças | `data/races.json` | Atributos iniciais |
| Catálogo de skills | `data/skills.json` | Nome, dano, cooldown |
| Catálogo de spells | `data/spells.json` | Nome, mana, efeito |
| Itens | `data/items.json` | Templates de item |
| Receitas | `data/recipes.json` | Materiais necessários |
| Áreas | `data/areas.json` | Descrição de áreas |
| Rooms | `data/rooms.json` | Blueprint de salas |
| NPCs | `data/npcs.json` | Specs de NPC |

**Exemplos:**
- ✅ Template de goblin → `backend/game/world/npc_templates.py` OU `data/npcs.json`
- ✅ Atributos de classe warrior → `data/classes.json`
- ✅ Fórmula de dano do warrior → `backend/config/balance.py` (lógica, não dados)
- ❌ Não criar `backend/game/world/classes.py` (use `data/classes.json`)
- ❌ Não criar `backend/data/` com Python (use JSON em `data/`)

---

#### 🧰 **Utilitários**

| O que é | Vai em | Padrão |
|---------|--------|--------|
| Utilitários gerais | `backend/utils/` | `logger.py`, `validators.py` |
| Utilitários de jogo | `backend/game/utils/` | `roll.py`, `formulas.py` |
| Tratamento de exceções | `backend/utils/exceptions.py` | Classes de erro customizadas |
| Logging | `backend/utils/logger.py` | Configuração de logs |

**Exemplos:**
- ✅ Validador de email → `backend/utils/validators.py`
- ✅ Sistema de dice rolls → `backend/game/utils/roll.py`
- ✅ Erro customizado de jogo → `backend/utils/exceptions.py`
- ❌ Não criar `backend/helpers/` (use `utils/`)
- ❌ Não criar `backend/common/` (seja específico)

---

#### 📝 **Documentação (Não código)**

| O que é | Vai em |
|---------|--------|
| Design do jogo | `DOCUMENTAÇÃO/GAME_DESIGN.md` |
| Mecânicas | `DOCUMENTAÇÃO/MECHANICS.md` |
| Regras de combate | `DOCUMENTAÇÃO/COMBAT_RULES.md` |
| Sistema de magia | `DOCUMENTAÇÃO/MAGIC_SYSTEM.md` |
| Sistema de crafting | `DOCUMENTAÇÃO/CRAFTING_SYSTEM.md` |
| Comportamentos de IA | `DOCUMENTAÇÃO/AI_BEHAVIOR.md` |
| Mapa do mundo | `DOCUMENTAÇÃO/WORLD_MAP.md` |
| Arquivo README | `README.md` (raiz do projeto) |
| Guia de arquitetura | `DOCUMENTAÇÃO/ARCHITECTURE.md` |

**NADA de lógica aqui. Apenas especificação.**

---

## Checklist: Arquivo está no lugar certo?

Antes de criar arquivo `X` para funcionalidade `Y`:

```
[ ] Isso é lógica de um motor específico?
    Sim → vai em backend/game/engines/[motor]/
    Não → próxima pergunta

[ ] Isso é um modelo de dados (classe Python)?
    Sim → vai em backend/models/
    Não → próxima pergunta

[ ] Isso é acesso a BD/ORM?
    Sim → vai em backend/db/ ou backend/game/engines/[motor]/db_interface.py
    Não → próxima pergunta

[ ] Isso é cache/Redis?
    Sim → vai em backend/cache/
    Não → próxima pergunta

[ ] Isso é IA/Ollama?
    Sim → vai em backend/ai/ (genérico) ou backend/game/engines/ai/ (motor)
    Não → próxima pergunta

[ ] Isso é configuração/constante?
    Sim → vai em backend/config/
    Não → próxima pergunta

[ ] Isso é handler/orquestração?
    Sim → vai em backend/handlers/
    Não → próxima pergunta

[ ] Isso é API/endpoint?
    Sim → vai em backend/api/
    Não → próxima pergunta

[ ] Isso é utilitário?
    Sim → vai em backend/utils/ ou backend/game/utils/
    Não → PARE e rethink!
```

---

## Exemplos de Estrutura Correta

### ✅ Adicionar novo motor (ex: Mount/Rideable)

```
backend/game/engines/mounts/
├── __init__.py
├── mounts.py              ← Orquestrador
├── mount_stats.py         ← Velocidade, resistência
├── speed_calc.py          ← Cálculo de movimento
├── db_interface.py        ← Acesso a mount data
└── utils.py               ← Helpers do motor
```

### ✅ Adicionar nova skill

```
Passo 1: Adiciona em data/skills.json
{
  "id": "fireball",
  "name": "Fireball",
  "damage": 50,
  "cooldown": 10
}

Passo 2: Não precisa criar arquivo novo!
- backend/game/engines/magic/magic.py detecta
- backend/game/engines/magic/spell_effects.py usa
- Automático!
```

### ✅ Adicionar novo efeito de combate

```
Arquivo: backend/game/engines/combat/effects.py

class GameEffect:
    """Efeito genérico"""
    pass

class BleedEffect(GameEffect):
    """Sangramento"""
    damage_per_tick = 5
    duration = 10

class StunEffect(GameEffect):
    """Atordoamento"""
    miss_chance = 100  # ação inválida
    duration = 3
```

---

## Anti-Patterns: O que NÃO fazer

❌ **Não criar pastas para conceitos genéricos**
```
Errado:
backend/game/
├── combat/     ← Pasta genérica
├── magic/      ← Pasta genérica
└── handlers/   ← Genérico

Certo: Use engines/
backend/game/engines/
├── combat/
├── magic/
└── [novo motor]/
```

❌ **Não espalhar lógica do motor em vários arquivos**
```
Errado:
backend/game/combat_logic.py
backend/handlers/combat_handler.py
backend/api/combat_routes.py
backend/db/combat_queries.py
← Tudo relacionado a combate espalhado

Certo: Tudo em
backend/game/engines/combat/
├── combat.py
├── damage_calc.py
├── db_interface.py
└── effects.py
```

❌ **Não criar sub-engines dentro de engines**
```
Errado:
backend/game/engines/combat/
├── sub_engines/
│   ├── damage/
│   ├── effects/
│   └── initialization/

Certo: Arquivos Python
backend/game/engines/combat/
├── damage_calc.py
├── effects.py
├── initialization.py
```

❌ **Não hardcode valores em código**
```
Errado:
if damage > 100:  # Número mágico no código!
    apply_crit()

Certo:
from config import CRIT_DAMAGE_THRESHOLD
if damage > CRIT_DAMAGE_THRESHOLD:
    apply_crit()
```

---

## Resumo Rápido: Onde vai cada tipo de arquivo?

| Tipo | Pasta | Padrão |
|------|-------|--------|
| Lógica de motor | `backend/game/engines/[motor]/` | `combat/`, `magic/`, `ai/` |
| Classe de modelo | `backend/models/` | `player.py`, `item.py` |
| BD/ORM | `backend/db/` | `models.py`, `queries.py` |
| Cache/Redis | `backend/cache/` | `redis_client.py`, `combat_cache.py` |
| IA/Ollama | `backend/ai/` | `ollama_service.py` |
| Handler/Orquestração | `backend/handlers/` | `command_handler.py` |
| API/Endpoint | `backend/api/` | `routes.py`, `websocket.py` |
| Configuração | `backend/config/` | `game_config.py`, `balance.py` |
| Templates/Dados | `backend/game/world/` + `data/` | JSONs + templates.py |
| Utilitários | `backend/utils/` ou `backend/game/utils/` | Helpers, validators |
| Testes | `tests/` (mesma estrutura) | `tests/engines/combat/` |
| Documentação | `DOCUMENTAÇÃO/` | Design docs, não código |

---

## Instruções para IA (Claude, etc)

**AO CRIAR UM NOVO ARQUIVO:**

1. **Antes de tudo:** Procure se já existe similar em:
   - `backend/game/engines/`
   - `backend/models/`
   - `backend/db/`
   - `backend/config/`

2. **Use a matriz acima** para decidir onde vai

3. **Se não encaixa perfeitamente:** 
   - Procure se cabe em `__init__.py` existente
   - Ou em `utils/` como utilitário
   - NÃO crie pasta nova sem autorização

4. **Ao renomear/mover arquivo:**
   - Atualize todos os imports
   - Teste se funciona
   - Documente o motivo

5. **Em caso de dúvida:**
   - Pergunte ao desenvolvedor (você)
   - Não suponha um local "que faz sentido"
   - Melhor redundância que dispersão

---

**LEMBRE:** Uma boa organização = código que não fica perdido + manutenção fácil + futuras features sem quebra.
