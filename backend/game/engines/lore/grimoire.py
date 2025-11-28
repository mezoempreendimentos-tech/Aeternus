# backend/game/engines/lore/grimoire.py
"""
O GRIMÓRIO VIVO - Motor de Mitologia Emergente

Este motor observa eventos épicos no mundo e os transforma em lendas
que se espalham organicamente através dos NPCs.
"""

import asyncio
import logging
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# ==============================================================================
# ESTRUTURAS DE DADOS
# ==============================================================================

@dataclass
class Legend:
    """Uma lenda que vive no mundo."""
    id: str  # UUID da lenda
    title: str  # "A Queda do Rato Gigante"
    category: str  # "heroic", "tragic", "comedic", "horror"
    protagonist: str  # Nome do jogador
    event_type: str  # "first_kill", "fatality", "death", "remort"
    
    # A história original (fatos puros)
    original_facts: Dict[str, Any]
    
    # Versões da história (como ela evolui)
    versions: List[str] = field(default_factory=list)
    
    # Metadados
    epic_score: int = 0  # Quão épica é (0-100)
    spread_count: int = 0  # Quantas vezes foi contada
    believers: List[str] = field(default_factory=list)  # NPCs que conhecem
    timestamp: float = field(default_factory=lambda: datetime.utcnow().timestamp())
    
    # Efeitos no mundo
    affects_reputation: bool = True
    zone_modifier: Optional[int] = None  # Zona onde aconteceu

@dataclass
class NPCMemory:
    """Memória de um NPC sobre lendas."""
    npc_uid: str
    known_legends: List[str] = field(default_factory=list)  # IDs de lendas
    favorite_story: Optional[str] = None
    storytelling_skill: int = 50  # 0-100, afeta qualidade das variações

# ==============================================================================
# MOTOR PRINCIPAL
# ==============================================================================

class GrimoireEngine:
    """
    O Escriba Eterno.
    Observa o mundo e tece mitologia.
    """
    
    def __init__(self, world_manager, ollama_service=None):
        self.world = world_manager
        self.ollama = ollama_service
        
        # Banco de Lendas
        self.legends: Dict[str, Legend] = {}
        self.npc_memories: Dict[str, NPCMemory] = {}
        
        # Configuração
        self.save_path = Path("data/grimoire.json")
        self.enabled = True
        
        # Filas de eventos
        self.pending_events: List[Dict] = []
        
    # ==========================================================================
    # CAPTURA DE EVENTOS
    # ==========================================================================
    
    async def witness_event(self, event_type: str, data: Dict[str, Any]):
        """
        Chamado quando algo épico acontece no mundo.
        
        Tipos de eventos:
        - "player_kill": Jogador mata NPC pela primeira vez
        - "fatality": Morte brutal/crítica
        - "death": Jogador morre
        - "remort": Jogador renasce
        - "discovery": Jogador descobre área secreta
        - "achievement": Feito único (solo boss, etc)
        """
        if not self.enabled:
            return
            
        logger.info(f"GRIMOIRE: Testemunhando evento '{event_type}'")
        
        # Calcula épica do evento
        epic_score = self._calculate_epic_score(event_type, data)
        
        # Se for épico o suficiente (>30), vira lenda
        if epic_score >= 30:
            legend = await self._create_legend(event_type, data, epic_score)
            self.legends[legend.id] = legend
            
            # Espalha para NPCs próximos
            await self._spread_to_witnesses(legend, data.get("location_vnum"))
            
            logger.info(f"GRIMOIRE: Nova lenda criada - '{legend.title}' (Épica: {epic_score})")
    
    def _calculate_epic_score(self, event_type: str, data: Dict) -> int:
        """
        Calcula quão épico é um evento (0-100).
        """
        score = 0
        
        # Base por tipo
        base_scores = {
            "first_kill": 40,
            "fatality": 70,
            "death": 50,
            "remort": 90,
            "discovery": 60,
            "boss_kill": 85,
            "pvp_kill": 75
        }
        score = base_scores.get(event_type, 20)
        
        # Modificadores contextuais
        if data.get("is_solo"):
            score += 20
        
        if data.get("player_level", 1) < data.get("enemy_level", 1):
            score += 15  # Underdog bonus
            
        if data.get("low_hp_clutch"):  # Vitória com <10% HP
            score += 25
            
        if data.get("weapon_type") == "unarmed":
            score += 30  # Matou desarmado!
            
        return min(100, score)
    
    # ==========================================================================
    # CRIAÇÃO DE LENDAS
    # ==========================================================================
    
    async def _create_legend(self, event_type: str, data: Dict, epic_score: int) -> Legend:
        """Cria uma nova lenda."""
        import uuid
        
        legend_id = str(uuid.uuid4())[:8]
        
        # Gera título épico
        title = self._generate_title(event_type, data)
        
        # Categoria
        category = self._categorize_event(event_type, data)
        
        # Versão 1: Os Fatos Puros
        original_version = self._narrate_facts(event_type, data)
        
        # Se temos Ollama, pede versão poética
        if self.ollama:
            try:
                poetic_version = await self._generate_poetic_version(event_type, data, original_version)
            except:
                poetic_version = original_version
        else:
            poetic_version = original_version
        
        legend = Legend(
            id=legend_id,
            title=title,
            category=category,
            protagonist=data.get("player_name", "Herói Desconhecido"),
            event_type=event_type,
            original_facts=data,
            versions=[original_version, poetic_version],
            epic_score=epic_score,
            zone_modifier=data.get("zone_id")
        )
        
        return legend
    
    def _generate_title(self, event_type: str, data: Dict) -> str:
        """Gera título épico."""
        player = data.get("player_name", "O Herói")
        
        templates = {
            "first_kill": [
                f"O Primeiro Sangue de {player}",
                f"{player} e a Iniciação Carmesim"
            ],
            "fatality": [
                f"A Execução Brutal de {player}",
                f"{player}, o Implacável"
            ],
            "death": [
                f"A Queda de {player}",
                f"Onde {player} Encontrou o Fim"
            ],
            "remort": [
                f"O Renascimento de {player}",
                f"{player}: O Ciclo Eterno"
            ]
        }
        
        options = templates.get(event_type, [f"A Saga de {player}"])
        return random.choice(options)
    
    def _categorize_event(self, event_type: str, data: Dict) -> str:
        """Determina a categoria narrativa."""
        if event_type in ["fatality", "boss_kill"]:
            return "heroic"
        elif event_type == "death" and data.get("embarrassing"):
            return "comedic"
        elif event_type == "death":
            return "tragic"
        elif data.get("is_dark_ritual"):
            return "horror"
        return "heroic"
    
    def _narrate_facts(self, event_type: str, data: Dict) -> str:
        """Narra os fatos de forma crônica."""
        player = data.get("player_name", "um aventureiro")
        location = data.get("location_name", "um lugar esquecido")
        
        if event_type == "fatality":
            enemy = data.get("enemy_name", "uma criatura")
            damage = data.get("damage", 0)
            return (
                f"No ano {data.get('year', 1000)}, {player} enfrentou {enemy} em {location}. "
                f"Com um golpe devastador de {damage} de dano, {player} executou o oponente "
                f"de forma brutal, cimentando sua reputação."
            )
        
        elif event_type == "death":
            killer = data.get("killer_name", "o destino")
            return (
                f"{player} caiu em {location}, vítima de {killer}. "
                f"Sua jornada terminou prematuramente, mas sua história permanece."
            )
        
        return f"{player} realizou um feito memorável em {location}."
    
    async def _generate_poetic_version(self, event_type: str, data: Dict, facts: str) -> str:
        """Usa Ollama para criar versão poética."""
        if not self.ollama:
            return facts
            
        prompt = f"""Você é um bardo medieval em uma taverna. 
Transforme este relato factual em uma narrativa épica de 2-3 frases, 
mantendo os fatos mas adicionando drama e poesia:

FATOS: {facts}

Escreva como se estivesse contando em uma taverna lotada. Use linguagem dramática mas não exagere."""
        
        try:
            poetic = await self.ollama.generate(prompt)
            return poetic.strip()
        except Exception as e:
            logger.error(f"Falha ao gerar versão poética: {e}")
            return facts
    
    # ==========================================================================
    # PROPAGAÇÃO DE LENDAS
    # ==========================================================================
    
    async def _spread_to_witnesses(self, legend: Legend, location_vnum: Optional[int]):
        """Espalha a lenda para NPCs que estavam presentes."""
        if not location_vnum:
            return
            
        room = self.world.get_room(location_vnum)
        if not room:
            return
        
        # Todos os NPCs na sala "ouviram"
        for npc_uid in room.npcs_here:
            npc = self.world.get_npc(npc_uid)
            if not npc:
                continue
                
            # Cria memória se não existe
            if npc_uid not in self.npc_memories:
                self.npc_memories[npc_uid] = NPCMemory(npc_uid=npc_uid)
            
            memory = self.npc_memories[npc_uid]
            
            # Adiciona lenda ao conhecimento
            if legend.id not in memory.known_legends:
                memory.known_legends.append(legend.id)
                legend.believers.append(npc_uid)
                legend.spread_count += 1
                
                logger.info(f"GRIMOIRE: {npc.name} agora conhece '{legend.title}'")
    
    async def spread_legend_naturally(self):
        """
        Tick periódico: NPCs compartilham histórias entre si.
        Chamado pelo TimeEngine a cada ~30 segundos.
        """
        if not self.legends:
            return
            
        # Escolhe uma sala aleatória com múltiplos NPCs
        populated_rooms = [r for r in self.world.rooms.values() if len(r.npcs_here) >= 2]
        
        if not populated_rooms:
            return
            
        room = random.choice(populated_rooms)
        
        # Escolhe um "contador de histórias"
        storyteller_uid = random.choice(room.npcs_here)
        storyteller_memory = self.npc_memories.get(storyteller_uid)
        
        if not storyteller_memory or not storyteller_memory.known_legends:
            return
            
        # Escolhe uma história para contar
        legend_id = random.choice(storyteller_memory.known_legends)
        legend = self.legends.get(legend_id)
        
        if not legend:
            return
            
        # "Conta" para outros NPCs na sala
        for listener_uid in room.npcs_here:
            if listener_uid == storyteller_uid:
                continue
                
            if listener_uid not in self.npc_memories:
                self.npc_memories[listener_uid] = NPCMemory(npc_uid=listener_uid)
            
            listener_memory = self.npc_memories[listener_uid]
            
            # Se já conhece, ignora
            if legend_id in listener_memory.known_legends:
                continue
                
            # Aprende a lenda (com possível distorção)
            listener_memory.known_legends.append(legend_id)
            legend.believers.append(listener_uid)
            legend.spread_count += 1
            
            # Log imersivo
            storyteller = self.world.get_npc(storyteller_uid)
            listener = self.world.get_npc(listener_uid)
            
            if storyteller and listener:
                logger.info(
                    f"GRIMOIRE: {storyteller.name} conta '{legend.title}' "
                    f"para {listener.name} em {room.title}"
                )
    
    # ==========================================================================
    # COMANDOS DE JOGADOR
    # ==========================================================================
    
    def get_legends_about_player(self, player_name: str) -> List[Legend]:
        """Retorna todas as lendas sobre um jogador."""
        return [l for l in self.legends.values() if l.protagonist.lower() == player_name.lower()]
    
    def get_zone_legends(self, zone_id: int) -> List[Legend]:
        """Retorna lendas de uma zona específica."""
        return [l for l in self.legends.values() if l.zone_modifier == zone_id]
    
    async def npc_tell_legend(self, npc_uid: str, legend_id: str) -> Optional[str]:
        """
        NPC conta uma lenda (possivelmente com variação).
        Retorna o texto narrativo.
        """
        memory = self.npc_memories.get(npc_uid)
        if not memory or legend_id not in memory.known_legends:
            return None
            
        legend = self.legends.get(legend_id)
        if not legend:
            return None
            
        npc = self.world.get_npc(npc_uid)
        npc_name = npc.name if npc else "Alguém"
        
        # Escolhe versão baseada na habilidade do NPC
        if memory.storytelling_skill > 70 and len(legend.versions) > 1:
            version = legend.versions[-1]  # Versão mais elaborada
        else:
            version = legend.versions[0]  # Versão factual
        
        # Adiciona introdução do NPC
        intros = [
            f"{npc_name} limpa a garganta e começa:",
            f"{npc_name} se inclina e sussurra:",
            f"Os olhos de {npc_name} brilham enquanto narra:",
            f"{npc_name} bate na mesa e declama:"
        ]
        
        intro = random.choice(intros)
        
        return f'{intro}\n"{version}"'
    
    # ==========================================================================
    # PERSISTÊNCIA
    # ==========================================================================
    
    def save_grimoire(self):
        """Salva todas as lendas em disco."""
        try:
            data = {
                "legends": {
                    lid: {
                        "id": l.id,
                        "title": l.title,
                        "category": l.category,
                        "protagonist": l.protagonist,
                        "event_type": l.event_type,
                        "original_facts": l.original_facts,
                        "versions": l.versions,
                        "epic_score": l.epic_score,
                        "spread_count": l.spread_count,
                        "believers": l.believers,
                        "timestamp": l.timestamp
                    }
                    for lid, l in self.legends.items()
                },
                "npc_memories": {
                    uid: {
                        "npc_uid": m.npc_uid,
                        "known_legends": m.known_legends,
                        "favorite_story": m.favorite_story,
                        "storytelling_skill": m.storytelling_skill
                    }
                    for uid, m in self.npc_memories.items()
                }
            }
            
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"GRIMOIRE: {len(self.legends)} lendas salvas.")
            
        except Exception as e:
            logger.error(f"Erro ao salvar grimório: {e}")
    
    def load_grimoire(self):
        """Carrega lendas do disco."""
        if not self.save_path.exists():
            logger.info("GRIMOIRE: Nenhum histórico encontrado. Começando limpo.")
            return
            
        try:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Restaura lendas
            for lid, ldata in data.get("legends", {}).items():
                self.legends[lid] = Legend(**ldata)
            
            # Restaura memórias
            for uid, mdata in data.get("npc_memories", {}).items():
                self.npc_memories[uid] = NPCMemory(**mdata)
            
            logger.info(f"GRIMOIRE: {len(self.legends)} lendas carregadas.")
            
        except Exception as e:
            logger.error(f"Erro ao carregar grimório: {e}")


# ==============================================================================
# INTEGRAÇÕES COM O MUNDO
# ==============================================================================

class GrimoireIntegration:
    """
    Hooks para integrar o Grimório com os sistemas existentes.
    """
    
    @staticmethod
    def hook_combat_manager(combat_manager, grimoire_engine):
        """Adiciona capturas de eventos no CombatManager."""
        
        original_handle_death = combat_manager._handle_death
        
        async def new_handle_death(entity_id, session, killer=None):
            # Chama original
            await original_handle_death(entity_id, session, killer)
            
            # Captura para Grimoire
            if killer:
                from backend.models.character import Character
                from backend.models.npc import NPCInstance
                
                if isinstance(killer, Character) and isinstance(
                    combat_manager._get_entity(entity_id), NPCInstance
                ):
                    victim = combat_manager._get_entity(entity_id)
                    
                    await grimoire_engine.witness_event("player_kill", {
                        "player_name": killer.name,
                        "player_level": killer.level,
                        "enemy_name": victim.name,
                        "enemy_level": victim.level,
                        "location_vnum": session.room_vnum,
                        "location_name": combat_manager.world.get_room(session.room_vnum).title,
                        "zone_id": victim.room_vnum // 100000,
                        "year": 1000  # Pegar do TimeEngine
                    })
        
        combat_manager._handle_death = new_handle_death