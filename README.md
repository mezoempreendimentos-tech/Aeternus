# AETERNUS MUD

Um MUD (Multi-User Dungeon) moderno construído com:
- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL + Redis
- **IA**: Ollama (Llama 3.2 7B)
- **WebSocket**: Socket.io para tempo real

## Estrutura do Projeto

```
aeternus/
├── DOCUMENTAÇÃO/          # Game Design Documents
├── backend/               # Código do servidor
│   ├── game/engines/      # Motores modulares
│   ├── db/                # ORM e queries
│   ├── config/            # Configurações
│   ├── api/               # Endpoints
│   └── main.py            # Entry point
├── data/                  # Dados do jogo (JSON)
├── tests/                 # Testes
└── docker-compose.yml     # Orquestração
```

## Quick Start

```bash
# 1. Clone repo
git clone https://github.com/seu-usuario/aeternus.git
cd aeternus

# 2. Setup
cp .env.example .env
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 3. Start services
docker-compose up -d

# 4. Run server
python3 backend/main.py
```

## Arquitetura

- **Engines**: Motores modulares (combate, magia, crafting, IA, etc)
- **Models**: Representação de dados do jogo
- **DB**: Camada de persistência
- **Cache**: Estado em tempo real
- **IA**: Integração com Ollama para NPCs

## Documentação

Leia `DOCUMENTAÇÃO/` para game design completo.

## Desenvolvimento

- Use `backend/game/engines/` para adicionar novas features
- Configure em `backend/config/balance.py`
- Dados em `data/` (JSONs)
- Testes em `tests/`

## Status

🚧 Em desenvolvimento - MVP Q4 2025

## Autor

Desenvolvido como projeto de nicho MUD moderno.
