Aqui está o **Grimório do Desenvolvedor: Aeternus**.  
Este documento contém o resumo técnico, as decisões de design e a estrutura de código de tudo o que construímos até agora. Salve este arquivo como AETERNUS\_DEV\_CONTEXT.md.  
Quando reiniciarmos em outra sessão, basta me enviar este arquivo (ou colar o conteúdo) e dizer: *"Aqui está o contexto do Aeternus"*, e eu saberei exatamente onde paramos.  
---

# **AETERNUS MUD \- Grimório do Desenvolvedor (v0.5)**

Status do Projeto: Core Engine Funcional (Simulação de Combate e Loop de Servidor Ativos).  
Tech Stack: Python 3.11+, FastAPI, Asyncio.

## **1\. Arquitetura de Pastas e Módulos**

O projeto segue uma arquitetura modular estrita definida no guia-organizacao.md.

backend/  
├── api/               \# Endpoints FastAPI (HTTP/WebSocket)  
├── config/            \# Configurações globais  
├── handlers/          \# Interpretadores de comandos (CommandContext)  
├── game/  
│   ├── commands/      \# Lógica dos verbos (core.py, progression.py)  
│   ├── world/         \# Gestão de Estado (world\_manager.py, factory.py)  
│   ├── utils/         \# Utilitários (vnum.py)  
│   └── engines/       \# Motores de Lógica Autônoma  
│       ├── ai/        \# (ecosystem.py, nemesis.py)  
│       ├── combat/    \# (manager.py, formulas.py, flavor.py)  
│       ├── leveling/  \# (leveling.py)  
│       └── time/      \# (manager.py, calendar.py, climate.py)  
└── models/            \# Dataclasses (character.py, npc.py, item.py, room.py)

## **2\. Conceitos Fundamentais**

### **Sistema VNUM (Virtual Number)**

* **Arquivo:** backend/game/utils/vnum.py  
* **Lógica:** Identificador único para Templates (Blueprints).  
* **Padrão:** ZZZXXXXX (Zona \[3 dígitos\] \+ ID Local \[5 dígitos\]). Ex: 100001\.  
* **Legado:** Suporta IDs antigos \<= 99999\.

### **Padrão Template vs. Instance**

Todos os objetos tangíveis seguem este padrão para escalabilidade:

* **Template (Blueprint):** Dados estáticos carregados de JSON (ex: NPCTemplate). Usa VNUM.  
* **Instance (Objeto Vivo):** Dados dinâmicos na memória (ex: NPCInstance). Usa UUID.  
  * *Ex:* Um ItemTemplate (Espada) não tem durabilidade gasta. Um ItemInstance tem.

---

## **3\. Motores de Jogo (Engines)**

### **A. Motor de Tempo (engines/time)**

* **Calendário:** 13 Meses de 28 Dias. Ano de 364 dias.  
* **Ritmo:** 1 Dia de Jogo \= 48 minutos reais (Multiplicador x30).  
* **Persistência:** Salva o estado em data/gamestate.json ao desligar o servidor para que o tempo não resete.  
* **Clima:** 7 Estações Globais cruzadas com Tipos de Zona (Ártico, Deserto, etc).

### **B. Motor de Combate (engines/combat)**

* **Tick:** Processado a cada 2 segundos.  
* **Juiz (manager.py):** Gerencia sessões de combate por sala.  
* **Fórmulas (formulas.py):**  
  * **Hit Chance:** Destreza/Sorte Atacante vs Destreza/Percepção Defensor.  
  * **Anatomia:** Seleciona parte do corpo baseada em pesos (Hit Weights).  
  * **Mitigação:** Considera Flags Materiais (MAT\_STONE resiste a slash).  
* **Flavor (flavor.py):** Narrador que gera textos descritivos.  
* **Eventos Especiais:**  
  * **Crítico (5%):** Dano x1.5.  
  * **Falha Crítica (5%):** Texto de vergonha (possível perda de turno futuro).  
  * **Fatality:** Se (Crítico E \[HP \< 10% OU Dano \> 80% Max\]), ocorre Morte Instantânea (Hit Kill) com descrição épica.  
  * **Severing (Decepar):** Dano massivo em membro SEVERABLE com arma SHARP corta o membro.

### **C. Motor de Nêmesis e Ecossistema (engines/ai)**

* **Nêmesis (nemesis.py):** NPCs ganham XP e Títulos ("o Matador de Noobs") ao matar jogadores. Podem evoluir de nível e virar Elites.  
* **Ecossistema (ecosystem.py):** Roda a cada 10s (Tick Global). Simula caça, fome e disputas territoriais entre NPCs quando jogadores não estão olhando. Define o **Alpha da Zona**.

### **D. Motor de Progressão (engines/leveling)**

* **Curva:** Geométrica suave (+8.0% XP req/nível).  
* **Meta:** \~54 Milhões de XP no Nível 100\.  
* **Ganhos:** XP por Dano, Tank, Cura e Kill (Baseado na Classe).  
* **Remort (Samsara):**  
  * Ao atingir Nível 100, jogador pode usar /renascer.  
  * Reseta para Nível 1, nova Classe.  
  * **Herança:** Escolhe 1 skill da vida anterior para manter permanentemente.  
  * **Custo:** \+10% de XP necessário por nível a cada Remort.

---

## **4\. Estrutura de Dados (JSONs)**

### **Anatomia (data/anatomy.json)**

Define corpos modulares.

JSON

"rodent": {  
  "parts": \[  
    {"id": "head", "name": "a Cabeça", "hit\_weight": 20, "hp\_factor": 0.2, "flags": \["VITAL"\]}  
  \]  
}

### **NPCs (data/npcs.json)**

Suporta ataques naturais se não tiver arma.

JSON

"natural\_attacks": \[  
  {"name": "Dentes", "damage\_type": "pierce", "verb": "morde", "damage\_mult": 1.0}  
\]

### **Salas (data/rooms.json)**

Suporta descrição sensorial e flags ambientais.

JSON

"sensory": { "visual": "Névoa baixa.", "olfactory": "Cheiro de enxofre." },  
"flags": \["INDOOR", "DARK"\]

---

## **5\. Comandos Implementados**

O CommandHandler suporta:

* **Informação:** olhar (l), inventario (i), equipamento (eq).  
* **Movimento:** Rosa dos ventos completa (N, S, L, O, NE, NO, SE, SO, Cima, Baixo).  
* **Combate:** matar \<alvo\> (k).  
* **Progressão:** renascer \<classe\> \<skill\> (Apenas em Altar de Criação).

---

## **6\. Como Rodar**

### **Modo Servidor (API \+ Game Loop)**

Bash

python \-m backend.main

* Endpoints:  
  * POST /api/command: Enviar comandos como jogador.  
  * GET /status: Ver estado do mundo/tempo.

### **Modo Simulação (Headless Battle Test)**

Bash

python simulate\_battle.py

* Cria dados temporários, spawna Heroi vs Rato e roda o combate round-a-round no console para testar fórmulas e leveling.

---

## **7\. Próximos Passos (Roadmap)**

1. **Persistência de Jogador:** Salvar/Carregar personagens do Banco de Dados (PostgreSQL/SQLite) em vez de criar na memória.  
2. **Sistema de Skills:** Implementar o uso ativo de skills (usar curar) além do ataque básico.  
3. **Inventário Real:** Comandos pegar, dropar, equipar.  
4. **Loot:** Fazer NPCs droparem itens no chão ao morrer (já previsto no código, falta implementar o spawn).