# backend/game/world/factory.py
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from backend.game.utils.vnum import VNum
from backend.models.item import ItemTemplate, ItemInstance, ItemDamage, ItemAttribute
from backend.models.npc import NPCTemplate, NPCInstance, BodyPartInstance, NaturalAttack
from backend.models.room import Room, RoomExit, RoomSensory

logger = logging.getLogger(__name__)

class ObjectFactory:
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self._item_templates: Dict[int, ItemTemplate] = {}
        self._npc_templates: Dict[int, NPCTemplate] = {}
        self._anatomy_templates: Dict[str, Any] = {} 
        self._room_templates: Dict[int, Room] = {} 

    def load_all_data(self):
        logger.info("Iniciando carregamento do mundo...")
        self._load_anatomy()
        self._load_items()
        self._load_npcs()
        self._load_rooms()
        logger.info(f"Mundo carregado: {len(self._item_templates)} Itens, {len(self._npc_templates)} NPCs, {len(self._room_templates)} Salas.")

    # ... (Outros loaders iguais) ...
    def _load_json(self, filename: str) -> Dict:
        path = self.data_path / filename
        if not path.exists(): return {}
        try:
            with open(path, 'r', encoding='utf-8') as f: return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler {filename}: {e}")
            return {}

    def _load_anatomy(self): self._anatomy_templates = self._load_json("anatomy.json")

    def _load_items(self):
        data = self._load_json("items.json")
        for vnum_str, data in data.items():
            try:
                vnum = int(vnum_str)
                damage_data = data.get("damage")
                damage_obj = ItemDamage(**damage_data) if damage_data else None
                attributes_list = [ItemAttribute(**attr) for attr in data.get("attributes", [])]

                template = ItemTemplate(
                    vnum=vnum,
                    name=data["name"],
                    description=data["description"],
                    type=data["type"],
                    rarity=data["rarity"],
                    slot=data.get("slot"),
                    damage=damage_obj,
                    armor_value=data.get("armor_value", 0),
                    weight=data.get("weight", 0.0),
                    base_value=data.get("value", 0),
                    flags=data.get("flags", []),
                    attack_verb=data.get("attack_verb"), # <--- Carregando verbo do item
                    requirements=data.get("requirements", {}),
                    attributes=attributes_list
                )
                self._item_templates[vnum] = template
            except Exception as e: logger.error(f"Erro Item {vnum_str}: {e}")

    def _load_npcs(self):
        data = self._load_json("npcs.json")
        for vnum_str, data in data.items():
            try:
                vnum = int(vnum_str)
                
                # Carrega ataques naturais
                nat_attacks = []
                for nat in data.get("natural_attacks", []):
                    nat_attacks.append(NaturalAttack(
                        name=nat["name"],
                        damage_type=nat["damage_type"],
                        verb=nat["verb"],
                        damage_mult=nat.get("damage_mult", 1.0)
                    ))

                template = NPCTemplate(
                    vnum=vnum,
                    name=data["name"],
                    description=data["description"],
                    level=data["level"],
                    base_hp=data.get("base_hp", 100),
                    body_type=data["body_type"],
                    sensory_visual=data.get("sensory_visual", "Nada."),
                    flags=data.get("flags", []),
                    loot_table=data.get("loot_table", {}),
                    sensory_auditory=data.get("sensory_auditory"),
                    natural_attacks=nat_attacks # <--- Carregando ataques naturais
                )
                self._npc_templates[vnum] = template
            except Exception as e: logger.error(f"Erro NPC {vnum_str}: {e}")

    def _load_rooms(self):
        data = self._load_json("rooms.json")
        for vnum_str, data in data.items():
            try:
                vnum = int(vnum_str)
                zone_id, _ = VNum.parse(vnum)
                sensory_data = data.get("sensory", {})
                sensory = RoomSensory(
                    visual=sensory_data.get("visual", "Nada."),
                    auditory=sensory_data.get("auditory"),
                    olfactory=sensory_data.get("olfactory"),
                    tactile=sensory_data.get("tactile"),
                    taste=sensory_data.get("taste")
                )
                
                exits = {}
                for direction, exit_data in data.get("exits", {}).items():
                    target_id = exit_data.get("target_id") or exit_data.get("target_vnum")
                    exits[direction] = RoomExit(
                        target_vnum=target_id,
                        direction=exit_data["direction"],
                        description=exit_data["description"],
                        is_locked=exit_data.get("is_locked", False),
                        key_vnum=exit_data.get("key_id"),
                        is_hidden=exit_data.get("is_hidden", False)
                    )

                room = Room(
                    vnum=vnum,
                    zone_id=zone_id,
                    title=data["title"],
                    description_day=data["description_day"],
                    description_night=data.get("description_night"),
                    sensory=sensory,
                    flags=data.get("flags", []),
                    exits=exits
                )
                self._room_templates[vnum] = room
            except Exception as e: logger.error(f"Erro Room {vnum_str}: {e}")

    # =========================================================================
    # FABRICATORS
    # =========================================================================

    def create_item_instance(self, vnum: int) -> Optional[ItemInstance]:
        template = self._item_templates.get(vnum)
        if not template: return None
        return ItemInstance(template_vnum=vnum, durability_current=template.durability_max)

    def create_npc_instance(self, vnum: int) -> Optional[NPCInstance]:
        template = self._npc_templates.get(vnum)
        if not template: return None

        instance = NPCInstance(
            template_vnum=vnum,
            name=template.name,
            level=template.level,
            total_hp=template.base_hp,
            current_hp=template.base_hp,
            flags=template.flags.copy()
        )
        self._build_npc_anatomy(instance, template)
        return instance

    def _build_npc_anatomy(self, instance: NPCInstance, template: NPCTemplate):
        body_def = self._anatomy_templates.get(template.body_type)
        if not body_def:
            body_def = self._anatomy_templates.get("humanoid")
            if not body_def: return

        parts_data = body_def.get("parts", [])
        for part_def in parts_data:
            p_id = part_def["id"]
            part_max_hp = int(template.base_hp * part_def.get("hp_factor", 0.1))
            
            part_instance = BodyPartInstance(
                definition_id=p_id,
                name=part_def["name"],
                hp_current=part_max_hp,
                hp_max=part_max_hp,
                flags=part_def.get("flags", []).copy()
            )
            instance.anatomy_state[p_id] = part_instance