# backend/game/world/world_manager.py
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.game.world.factory import ObjectFactory
from backend.models.room import Room
from backend.models.character import Character
from backend.models.npc import NPCInstance
from backend.models.item import ItemInstance
from backend.models.area import Area, AreaEcology # Se criamos o arquivo area.py, importamos aqui. Se não, usamos dict simples.
from backend.game.utils.vnum import VNum

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
        self.players: Dict[int, Character] = {}   # PlayerID -> Character Object
        self.active_npcs: Dict[str, NPCInstance] = {}    # UUID -> NPC Object
        self.active_items: Dict[str, ItemInstance] = {}  # UUID -> Item Object
        
        # Estado das Zonas (Ecossistema)
        # ZoneID (int) -> Dict com dados do Alpha, nível de ameaça, etc.
        self.zone_states: Dict[int, Dict[str, Any]] = {}

        # Estado Global
        self.is_daytime: bool = True

    async def start_up(self):
        """Inicializa o mundo, carrega dados e popula o estado inicial."""
        logger.info("WorldManager: Iniciando sequência de gênesis...")
        
        # 1. Carrega Blueprints
        self.factory.load_all_data()
        
        # 2. Popula Salas (Instância as salas estáticas)
        self.rooms = self.factory._room_templates
        
        # 3. Inicializa Estados de Zona
        self._init_zones()
        
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
        return self.rooms.get(vnum)

    def get_player(self, player_id: int) -> Optional[Character]:
        return self.players.get(player_id)

    def get_npc(self, uid: str) -> Optional[NPCInstance]:
        return self.active_npcs.get(uid)

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
            # Fallback para sala inicial segura (ex: 100001 ou 3001 legacy)
            character.location_vnum = 1 # Exemplo
            # Lógica de fallback real necessária aqui

    def remove_player(self, player_id: int):
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
        
        # Se era o Alpha, a zona fica órfã
        zone_id, _ = VNum.parse(npc.room_vnum)
        zone = self.zone_states.get(zone_id)
        if zone and zone["current_alpha_uid"] == uid:
            zone["current_alpha_uid"] = None
            zone["alpha_title"] = None
            # Broadcast para a zona inteira poderia ocorrer aqui: "O Tirano caiu!"

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

    def move_character(self, player_id: int, target_vnum: int) -> bool:
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
            # Aqui poderíamos aumentar o threat_level da zona
            self.zone_states[zone_id]["threat_level"] += 1