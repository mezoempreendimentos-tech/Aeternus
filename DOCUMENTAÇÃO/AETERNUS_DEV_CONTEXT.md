Salve, Escriba do Destino.

Você tem toda a razão. O conhecimento que não é registrado está fadado a se perder nas areias do tempo. O Grimório está vivo, os bardos cantam, e a Inteligência Artificial sonha dentro do seu servidor. Isso marca o fim de uma Era e o início de outra.

Aqui está o **AETERNUS\_DEV\_CONTEXT.md** atualizado para a versão **v0.70**. Ele documenta a infraestrutura do Grimório, a integração com Ollama/Docker e os novos comandos.

Salve este arquivo para que, no futuro, saibamos como a magia foi tecida.

````markdown
# **AETERNUS MUD - Grimório do Desenvolvedor (v0.70)**

**Status do Projeto:** Persistência Sólida, Inventário Real, Acesso Híbrido, Sistema de Lore (Grimório) e IA Generativa Funcional.
**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy (SQLite), Asyncio, Docker (Ollama/TinyLlama).

---

## **1. Arquitetura de Pastas e Módulos**

O projeto segue a arquitetura modular estrita definida no `guia-organizacao.md`.

```text
raiz/
├── aeternus.db        # O Sarcófago (Banco de Dados SQLite)
├── client.py          # Portal de Acesso (Cliente HTTP)
├── init_db.py         # Ritual de Gênesis (Cria tabelas)
├── delete_player.py   # Ritual de Banimento
├── simulate_lore.py   # Simulação de Lendas e IA (Novo)
├── simulate_battle.py # Simulação de Combate Headless
├── docker-compose.yml # Orquestração da IA
├── backend/
│   ├── api/           # (routes.py, telnet.py)
│   ├── config/        # (server_config.py - Configs de IA incluídas)
│   ├── ai/            # (ollama_service.py - Cliente HTTP para IA)
│   ├── db/            # (base.py, models.py, queries.py)
│   ├── handlers/      # (command_handler.py)
│   ├── game/
│   │   ├── commands/  # (core.py, progression.py, lore.py)
│   │   ├── world/     # (world_manager.py - Gerencia Grimoire)
│   │   ├── engines/   # Motores de Lógica
│   │   │   ├── ai/    # (nemesis.py, ecosystem.py)
│   │   │   ├── combat/# (manager.py - Hooks para Fatalities)
│   │   │   ├── lore/  # (grimoire.py - O Cérebro das Lendas)
│   │   │   └── time/  # (manager.py - Propagação de Fofoca)
│   └── models/        # (Player, ItemInstance, NPCInstance)
````

-----

## **2. O Grimório Vivo (Sistema de Lore & IA)**

Uma camada de narrativa emergente que transforma eventos de gameplay em mitologia.

### **Fluxo da Lenda**

1.  **Evento:** Algo épico acontece (ex: Fatality, Boss Kill, Remort).
2.  **Testemunha:** O `GrimoireEngine` captura os dados brutos.
3.  **Poesia (IA):** O `OllamaService` envia os dados para o modelo **TinyLlama** (via Docker), que retorna uma descrição dramática.
4.  **Cristalização:** Uma `Legend` é criada e salva em `data/grimoire.json`.
5.  **Propagação:** O `TimeEngine` periodicamente faz NPCs na mesma sala "conversarem", transferindo lendas para suas memórias (`NPCMemory`).
6.  **Interação:** Jogadores podem ouvir essas lendas dos NPCs.

### **Comandos de Lore**

  * `lendas`: Lista as histórias mais famosas do mundo ou de uma zona.
  * `ouvir <npc>`: Pede para um NPC contar uma história (usa IA se disponível).
  * `reputacao <player>`: Mostra o nível de fama e feitos de um jogador.
  * `mitos`: Estatísticas globais do servidor.

-----

## **3. Infraestrutura de Inteligência Artificial**

Para o Grimório funcionar com poesia, o **Ollama** deve estar rodando via Docker.

**Setup Rápido (Windows/PowerShell):**

1.  **Subir Serviço:** `docker compose up -d ollama`
2.  **Baixar Cérebro:** `docker compose exec ollama ollama pull tinyllama`
      * *Nota:* Usamos `tinyllama` por ser rápido e leve para testes. `llama2` é melhor mas mais lento.
3.  **Configuração:** Ajustar `OLLAMA_MODEL` em `backend/config/server_config.py`.

-----

## **4. Camada de Persistência**

  * **DB:** SQLite (`aeternus.db`) com SQLAlchemy.
  * **Identidade:** UUIDs para jogadores.
  * **Inventário:** Itens são serializados em JSON no banco e hidratados em Objetos na memória ao logar.
  * **Autenticação:** Senha simples exigida no Registro e Login (Telnet e API).

-----

## **5. Conectividade Híbrida**

  * **API REST (8000):** Para painéis e clientes web.
  * **Telnet (4000):** Para MUD Clients clássicos (MUSHClient, Mudlet). O servidor Telnet roda em uma Task Asyncio paralela ao FastAPI.

-----

## **6. Como Rodar (Workflow v0.70)**

1.  **Gênesis (1ª vez):** `python init_db.py`
2.  **IA (Opcional mas recomendado):** Garantir que o Docker do Ollama esteja rodando.
3.  **Servidor:** `python -m backend.main`
      * *Aguarde:* "AETERNUS ONLINE", "PORTAL TELNET ABERTO" e "Grimório Vivo ativado".
4.  **Jogar:** Conectar via Telnet (`localhost:4000`) ou usar `python client.py`.

-----

## **7. Próximos Passos (Roadmap)**

1.  **Sistema de Skills Ativas:**
      * Implementar `/cast`, custos de mana, cooldowns e efeitos (dano direto, cura, buffs).
      * Criar arquitetura de `Spell` e `Skill` nas engines.
2.  **Loot de Mobs:**
      * Criar container "Corpo" ao morrer.
      * Gerar loot tables básicas.
3.  **Refinamento de Combate:**
      * Adicionar skills ao loop de combate automático.

<!-- end list -->

```

Com este documento salvo, qualquer engenheiro (ou eu mesmo, no futuro) saberá exatamente como operar a torre de Aeternus.

**O trabalho de hoje está concluído? Devo me retirar para as sombras?**
```