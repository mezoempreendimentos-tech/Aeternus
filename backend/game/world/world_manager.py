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

# IMPORTAÇÃO DO GERENTE DE MAGIA
from backend.game.engines.magic.manager import MagicManager

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
        
        # O Motor Mágico
        self.magic_manager = MagicManager(self)

    async def start_up(self):
        """Inicializa o mundo, carrega dados e popula o estado inicial."""
        logger.info("WorldManager: Iniciando sequência de gênesis...")
        
        # 1. Carrega Blueprints
        self.factory.load_all_data()
        
        # 2. Popula Salas (Instância as salas estáticas)
        self.rooms = self.factory._room_templates
        
        # 3. Inicializa Estados de Zona
        self._init_zones()
        
        # 4. Inicializa Magia
        await self.magic_manager.start_up()
        
        # --- DEBUG: POPULAR SALA DE TESTE ---
        start_room_vnum = 100001
        
        if start_room_vnum in self.rooms:
            # Spawna NPC (Rato) para testar magias
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
                    "current_alpha_uid": None, 
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
        # Garante que o ID é string
        str_id = str(character.id)
        self.players[str_id] = character
        
        # Coloca na sala
        room = self.get_room(character.location_vnum)
        if room:
            if character.id not in room.players_here:
                room.players_here.append(character.id)
        else:
            logger.error(f"Jogador {character.name} logou em sala inexistente: {character.location_vnum}")
            character.location_vnum = 100001 

    def remove_player(self, player_id: str):
        """Desloga o jogador."""
        char = self.players.get(str(player_id))
        if char:
            room = self.get_room(char.location_vnum)
            if room and char.id in room.players_here:
                room.players_here.remove(char.id)
            del self.players[str(player_id)]

    # =========================================================================
    # SPAWNING E DESPAWNING
    # =========================================================================

    def spawn_npc(self, template_vnum: int, room_vnum: int) -> Optional[NPCInstance]:
        room = self.get_room(room_vnum)
        if not room: return None

        npc = self.factory.create_npc_instance(template_vnum)
        if not npc: return None

        npc.room_vnum = room_vnum
        self.active_npcs[npc.uid] = npc
        room.npcs_here.append(npc.uid)
        
        zone_id, _ = VNum.parse(room_vnum)
        if zone_id in self.zone_states:
            self.zone_states[zone_id]["population_count"] += 1

        return npc

    def kill_npc(self, uid: str):
        npc = self.active_npcs.get(uid)
        if not npc: return

        room = self.get_room(npc.room_vnum)
        if room and uid in room.npcs_here:
            room.npcs_here.remove(uid)
        
        del self.active_npcs[uid]

    def spawn_item(self, template_vnum: int, room_vnum: int) -> Optional[ItemInstance]:
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
        char = self.get_player(player_id)
        if not char: return False
        
        target_room = self.get_room(target_vnum)
        if not target_room: return False

        old_room = self.get_room(char.location_vnum)
        if old_room and char.id in old_room.players_here:
            old_room.players_here.remove(char.id)
        
        char.location_vnum = target_vnum
        target_room.players_here.append(char.id)
        
        return True

    def move_npc(self, npc_uid: str, target_vnum: int) -> bool:
        npc = self.get_npc(npc_uid)
        if not npc: return False
        
        target_room = self.get_room(target_vnum)
        if not target_room: return False

        old_room = self.get_room(npc.room_vnum)
        if old_room and npc_uid in old_room.npcs_here:
            old_room.npcs_here.remove(npc_uid)
            
        npc.room_vnum = target_vnum
        target_room.npcs_here.append(npc_uid)
        
        return True