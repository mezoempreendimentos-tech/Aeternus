# backend/game/world/world_manager.py
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.game.world.factory import ObjectFactory
from backend.models.room import Room
from backend.models.character import Character
from backend.models.npc import NPCInstance
from backend.models.item import ItemInstance
from backend.game.utils.vnum import VNum

# NOVO: Importação do Motor de Lore
from backend.game.engines.lore.grimoire import GrimoireEngine

logger = logging.getLogger(__name__)

class WorldManager:
    """
    O Guardião do Estado do Mundo.
    Mantém todas as entidades vivas, controla movimentação e persistência em memória.
    """

    def __init__(self):
        self.factory = ObjectFactory()
        
        # --- ESTADO DO MUNDO ---
        self.rooms: Dict[int, Room] = {}          # VNUM -> Room Object
        
        # Entidades Ativas (Na memória RAM)
        self.players: Dict[str, Character] = {}   # PlayerID (str) -> Character Object
        self.active_npcs: Dict[str, NPCInstance] = {}    # UUID -> NPC Object
        self.active_items: Dict[str, ItemInstance] = {}  # UUID -> Item Object
        
        # Estado das Zonas (Ecossistema)
        self.zone_states: Dict[int, Dict[str, Any]] = {}

        # Estado Global
        self.is_daytime: bool = True
        
        # NOVO: O Grimório Vivo
        self.grimoire: Optional[GrimoireEngine] = None

    async def start_up(self):
        """Inicializa o mundo, carrega dados e popula o estado inicial."""
        logger.info("WorldManager: Iniciando sequência de gênesis...")
        
        # 1. Carrega Blueprints
        self.factory.load_all_data()
        
        # 2. Popula Salas (Instância as salas estáticas)
        self.rooms = self.factory._room_templates
        
        # 3. Inicializa Estados de Zona
        self._init_zones()
        
        # NOVO: Inicializa Grimório (após carregar factory)
        # Importação tardia para evitar ciclos
        try:
            from backend.ai.ollama_service import OllamaService
            ollama = OllamaService()
        except ImportError:
            logger.warning("OllamaService não encontrado. Grimório rodará sem IA.")
            ollama = None
        except Exception as e:
            logger.warning(f"IA Ollama indisponível: {e}. O Grimório operará em modo passivo.")
            ollama = None
        
        self.grimoire = GrimoireEngine(self, ollama)
        self.grimoire.load_grimoire()
        
        logger.info("📜 Grimório Vivo ativado.")
        
        # --- DEBUG: POPULAR SALA DE TESTE ---
        start_room_vnum = 100001
        debug_item_vnum = 100001
        
        if start_room_vnum in self.rooms:
            # Spawna Item
            item = self.spawn_item(debug_item_vnum, start_room_vnum)
            if item:
                logger.info(f"⚔️ DEBUG: {item.custom_name or 'Item'} spawnado na sala {start_room_vnum}.")
            
            # Spawna NPC (Rato) para garantir que há vida
            mob = self.spawn_npc(100001, start_room_vnum)
            if mob:
                logger.info(f"🐀 DEBUG: {mob.name} spawnado na sala {start_room_vnum}.")
        else:
            logger.warning("⚠️ Sala de Teste 100001 não encontrada! Verifique rooms.json.")
        
        logger.info("WorldManager: Mundo online.")

    def _init_zones(self):
        """Identifica todas as zonas presentes e cria seus estados ecológicos."""
        for vnum in self.rooms.keys():
            zone_id, _ = VNum.parse(vnum)
            if zone_id not in self.zone_states:
                self.zone_states[zone_id] = {
                    "threat_level": 1,
                    "current_alpha_uid": None, # UUID do NPC Alpha
                    "alpha_title": None,
                    "population_count": 0
                }

    # =========================================================================
    # GERENCIAMENTO DE ENTIDADES
    # =========================================================================

    def get_room(self, vnum: int) -> Optional[Room]:
        return self.rooms.get(int(vnum))

    def get_player(self, player_id: str) -> Optional[Character]:
        return self.players.get(str(player_id))

    def get_npc(self, uid: str) -> Optional[NPCInstance]:
        return self.active_npcs.get(uid)
        
    def get_item(self, uid: str) -> Optional[ItemInstance]:
        return self.active_items.get(uid)

    def add_player(self, character: Character):
        """Loga o jogador no mundo."""
        self.players[character.id] = character
        
        # Coloca na sala
        room = self.get_room(character.location_vnum)
        if room:
            if character.id not in room.players_here:
                room.players_here.append(character.id)
        else:
            logger.error(f"Jogador {character.name} logou em sala inexistente: {character.location_vnum}")
            # Fallback para sala inicial segura
            character.location_vnum = 100001 

    def remove_player(self, player_id: str):
        """Desloga o jogador (apenas da memória do mundo)."""
        char = self.players.get(player_id)
        if char:
            room = self.get_room(char.location_vnum)
            if room and player_id in room.players_here:
                room.players_here.remove(player_id)
            del self.players[player_id]

    # =========================================================================
    # SPAWNING E DESPAWNING
    # =========================================================================

    def spawn_npc(self, template_vnum: int, room_vnum: int) -> Optional[NPCInstance]:
        """Cria um NPC e o coloca em uma sala."""
        room = self.get_room(room_vnum)
        if not room:
            logger.warning(f"Tentativa de spawn em sala inválida: {room_vnum}")
            return None

        npc = self.factory.create_npc_instance(template_vnum)
        if not npc:
            return None

        # Configura Localização
        npc.room_vnum = room_vnum
        
        # Registra no Mundo
        self.active_npcs[npc.uid] = npc
        room.npcs_here.append(npc.uid)
        
        # Atualiza censo da zona
        zone_id, _ = VNum.parse(room_vnum)
        if zone_id in self.zone_states:
            self.zone_states[zone_id]["population_count"] += 1

        return npc

    def kill_npc(self, uid: str):
        """Remove o NPC do mundo (Morte Permanente da Instância)."""
        npc = self.active_npcs.get(uid)
        if not npc:
            return

        # Remove da sala
        room = self.get_room(npc.room_vnum)
        if room and uid in room.npcs_here:
            room.npcs_here.remove(uid)
        
        # Se era o Alpha, a zona fica órfã (Lógica simplificada)
        del self.active_npcs[uid]

    def spawn_item(self, template_vnum: int, room_vnum: int) -> Optional[ItemInstance]:
        """Cria um item e joga no chão da sala."""
        room = self.get_room(room_vnum)
        if not room: return None

        item = self.factory.create_item_instance(template_vnum)
        if not item: return None

        item.room_vnum = room_vnum
        self.active_items[item.uid] = item
        room.items_here.append(item.uid)
        
        return item

    # =========================================================================
    # MOVIMENTAÇÃO
    # =========================================================================

    def move_character(self, player_id: str, target_vnum: int) -> bool:
        """
        Move um jogador de uma sala para outra.
        Retorna True se sucesso.
        """
        char = self.get_player(player_id)
        if not char: return False
        
        target_room = self.get_room(target_vnum)
        if not target_room: return False

        # 1. Sai da sala antiga
        old_room = self.get_room(char.location_vnum)
        if old_room and player_id in old_room.players_here:
            old_room.players_here.remove(player_id)
        
        # 2. Entra na nova
        char.location_vnum = target_vnum
        target_room.players_here.append(player_id)
        
        return True

    def move_npc(self, npc_uid: str, target_vnum: int) -> bool:
        """Move NPC (usado pelo EcosystemEngine para migração)."""
        npc = self.get_npc(npc_uid)
        if not npc: return False
        
        target_room = self.get_room(target_vnum)
        if not target_room: return False

        # Sai da antiga
        old_room = self.get_room(npc.room_vnum)
        if old_room and npc_uid in old_room.npcs_here:
            old_room.npcs_here.remove(npc_uid)
            
        # Entra na nova
        npc.room_vnum = target_vnum
        target_room.npcs_here.append(npc_uid)
        
        return True

    # =========================================================================
    # SISTEMA DE INVENTÁRIO
    # =========================================================================
    
    def pick_up_item(self, player_id: str, item_uid: str) -> bool:
        """Transfere item do CHÃO para o INVENTÁRIO."""
        player = self.get_player(player_id)
        item = self.get_item(item_uid)
        room = self.get_room(player.location_vnum)

        if not player or not item or not room:
            return False
            
        # Validação: Item está mesmo na sala?
        if item_uid not in room.items_here:
            return False

        # 1. Remove da Sala
        room.items_here.remove(item_uid)
        item.room_vnum = None
        
        # 2. Adiciona ao Player
        player.inventory.append(item_uid)
        item.owner_character_id = player_id
        item.container_uid = "inventory"
        
        return True

    def drop_item(self, player_id: str, item_uid: str) -> bool:
        """Transfere item do INVENTÁRIO para o CHÃO."""
        player = self.get_player(player_id)
        item = self.get_item(item_uid)
        room = self.get_room(player.location_vnum)

        if not player or not item or not room:
            return False

        # Validação: Item está com o player?
        if item_uid not in player.inventory:
            return False

        # 1. Remove do Player
        player.inventory.remove(item_uid)
        item.owner_character_id = None
        item.container_uid = None
        
        # 2. Adiciona à Sala
        room.items_here.append(item_uid)
        item.room_vnum = room.vnum
        
        return True

    # =========================================================================
    # ECOSSISTEMA E ZONAS
    # =========================================================================

    def get_zone_alpha(self, zone_id: int) -> Optional[NPCInstance]:
        """Retorna o objeto NPC que é o atual Alpha da zona."""
        state = self.zone_states.get(zone_id)
        if not state or not state["current_alpha_uid"]:
            return None
        return self.get_npc(state["current_alpha_uid"])

    def set_zone_alpha(self, zone_id: int, npc: NPCInstance):
        """Define o novo Alpha da região."""
        if zone_id in self.zone_states:
            self.zone_states[zone_id]["current_alpha_uid"] = npc.uid
            self.zone_states[zone_id]["alpha_title"] = npc.full_name
            self.zone_states[zone_id]["threat_level"] += 1