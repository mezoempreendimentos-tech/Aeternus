# backend/game/engines/combat/manager.py
import logging
import random
import asyncio
from typing import Dict, List, Optional, Set

from backend.game.world.world_manager import WorldManager
from backend.game.engines.combat.formulas import CombatFormulas
from backend.game.engines.combat.flavor import CombatNarrator
from backend.game.engines.leveling.leveling import LevelingEngine
from backend.models.character import Character
from backend.models.npc import NPCInstance, BodyPartInstance
from backend.models.item import ItemInstance, ItemTemplate, ItemDamage

logger = logging.getLogger(__name__)

class CombatSession:
    def __init__(self, room_vnum: int):
        self.room_vnum = room_vnum
        self.participants: Set[str] = set() 
        self.targets: Dict[str, str] = {}
        self.round_log: List[str] = []

    def add_participant(self, entity_id: str, target_id: str):
        self.participants.add(entity_id)
        self.participants.add(target_id)
        self.targets[entity_id] = target_id
        if target_id not in self.targets:
            self.targets[target_id] = entity_id

    def is_active(self):
        return len(self.participants) >= 2

class CombatManager:
    def __init__(self, world_manager: WorldManager):
        self.world = world_manager
        self.sessions: Dict[int, CombatSession] = {}

    async def start_combat(self, attacker, defender):
        att_id = self._get_id(attacker)
        def_id = self._get_id(defender)
        room_vnum = attacker.location_vnum if isinstance(attacker, Character) else attacker.room_vnum
        
        session = self.sessions.get(room_vnum)
        if not session:
            session = CombatSession(room_vnum)
            self.sessions[room_vnum] = session
            
        session.add_participant(att_id, def_id)
        name_att = attacker.name
        name_def = defender.name
        self._broadcast_to_room(room_vnum, f"\n⚔️ {name_att} INICIOU COMBATE CONTRA {name_def}!\n")

    async def process_round(self):
        if not self.sessions: return
        for room_vnum in list(self.sessions.keys()):
            session = self.sessions[room_vnum]
            await self._resolve_session(session)
            if not session.is_active():
                del self.sessions[room_vnum]

    async def _resolve_session(self, session: CombatSession):
        session.round_log.clear()
        dead_entities = set()

        for entity_id in list(session.participants):
            if entity_id in dead_entities: continue
            attacker = self._get_entity(entity_id)
            target_id = session.targets.get(entity_id)
            defender = self._get_entity(target_id)

            if not attacker or not defender:
                session.participants.discard(entity_id)
                continue
                
            if not self._is_alive(attacker) or not self._is_alive(defender):
                continue

            self._execute_attack(attacker, defender, session, dead_entities)

        if session.round_log:
            msg = "\n".join(session.round_log)
            self._broadcast_to_room(session.room_vnum, msg)

    def _execute_attack(self, attacker, defender, session, dead_set):
        weapon_tmpl = self._determine_attack_source(attacker)
        weapon_name = weapon_tmpl.name
        weapon_flags = weapon_tmpl.flags

        hit_chance = CombatFormulas.calculate_hit_chance(attacker, defender, weapon_tmpl)
        roll = random.random()

        if roll >= 0.95:
            fumble_msg = CombatNarrator.get_fumble(attacker.name)
            session.round_log.append(f"❌ {fumble_msg}")
            return

        if roll > hit_chance:
            session.round_log.append(f"{attacker.name} tenta atacar com {weapon_name}, mas {defender.name} esquiva!")
            return

        part_id, body_part = CombatFormulas.select_body_part(defender)
        part_name = body_part.name if body_part else "o corpo"

        is_crit = (roll <= 0.05)
        dmg_info = CombatFormulas.calculate_damage(attacker, weapon_tmpl, is_crit)
        final_damage = CombatFormulas.calculate_mitigation(defender, dmg_info, body_part)

        is_fatality = False
        if is_crit:
            if isinstance(defender, Character):
                hp, max_hp = defender.hp.current, defender.hp.maximum
            else:
                hp, max_hp = defender.current_hp, defender.total_hp

            if hp <= (max_hp * 0.10) or final_damage >= (max_hp * 0.80):
                is_fatality = True
                final_damage = hp 

        self._apply_damage(defender, body_part, final_damage, attacker)

        severed_msg = ""
        if body_part and CombatFormulas.check_severing(final_damage, body_part, weapon_flags):
            body_part.is_severed = True
            severed_msg = f" DECEPANDO {part_name.upper()}!"

        if is_fatality:
            flavor = CombatNarrator.get_fatality(attacker.name, defender.name, dmg_info['type'])
            log_entry = f"🩸 FATALITY! {flavor} ({final_damage} dano!){severed_msg}"
        else:
            crit_str = " CRITICAMENTE" if is_crit else ""
            verb = weapon_tmpl.attack_verb or self._get_damage_verb(dmg_info['type'], final_damage)
            log_entry = f"{attacker.name} {verb} {part_name} de {defender.name}{crit_str} ({final_damage}){severed_msg}."
        
        session.round_log.append(log_entry)

        if not self._is_alive(defender):
            dead_set.add(self._get_id(defender))
            asyncio.create_task(self._handle_death(self._get_id(defender), session, killer=attacker))

    def _determine_attack_source(self, attacker) -> ItemTemplate:
        real_weapon = self._get_equipped_weapon(attacker)
        if real_weapon: return real_weapon

        if isinstance(attacker, NPCInstance):
            template = self.world.factory._npc_templates.get(attacker.template_vnum)
            if template and template.natural_attacks:
                nat = random.choice(template.natural_attacks)
                base_min = max(1, int(attacker.level * 1.5))
                base_max = max(2, int(attacker.level * 2.5))
                
                return ItemTemplate(
                    vnum=0, name=nat.name, description="Arma Natural", 
                    type="natural", rarity="common", slot=None,
                    damage=ItemDamage(
                        min_dmg=int(base_min * nat.damage_mult),
                        max_dmg=int(base_max * nat.damage_mult),
                        damage_type=nat.damage_type
                    ),
                    attack_verb=nat.verb
                )

        return ItemTemplate(
            vnum=0, name="Punhos Nus", description="", type="unarmed", rarity="junk", slot=None,
            damage=ItemDamage(min_dmg=1, max_dmg=2, damage_type="blunt"),
            attack_verb="soca"
        )

    def _apply_damage(self, entity, body_part: Optional[BodyPartInstance], amount: int, attacker=None):
        if isinstance(entity, Character):
            entity.hp.current = max(0, entity.hp.current - amount)
        else:
            entity.current_hp = max(0, entity.current_hp - amount)
        
        if body_part:
            body_part.hp_current = max(0, body_part.hp_current - amount)
            if body_part.hp_current == 0 and not body_part.is_broken:
                body_part.is_broken = True

        if attacker and isinstance(attacker, Character):
            target_lvl = getattr(entity, 'level', 1)
            xp = LevelingEngine.calculate_xp_gain(attacker, "damage", amount, target_lvl)
            msgs = LevelingEngine.award_xp(attacker, xp)
            if msgs: logger.info(f"LEVEL UP: {attacker.name} -> {attacker.level}")

        if isinstance(entity, Character) and self._is_alive(entity):
            attacker_lvl = getattr(attacker, 'level', 1)
            xp = LevelingEngine.calculate_xp_gain(entity, "tank", amount, attacker_lvl)
            LevelingEngine.award_xp(entity, xp)

    async def _handle_death(self, entity_id: str, session: CombatSession, killer=None):
        entity = self._get_entity(entity_id)
        if not entity: return
        if entity_id not in session.participants: return

        room_vnum = session.room_vnum
        session.participants.discard(entity_id)
        if entity_id in session.targets:
            del session.targets[entity_id]

        self._broadcast_to_room(room_vnum, f"\n💀 {entity.name} CAIU MORTO!\n")

        if killer and isinstance(killer, Character) and isinstance(entity, NPCInstance):
            xp = LevelingEngine.calculate_xp_gain(killer, "kill", 0, entity.level)
            msgs = LevelingEngine.award_xp(killer, xp)
            logger.info(f"KILL XP: {killer.name} ganhou {xp} XP. Msgs: {msgs}")
            
            # === [MODIFICADO] DROP DE CATALISADORES ===
            # Adiciona chance de drop de item mágico ao matar mob
            import random
            if random.random() < 0.4:
                sys = self.world.magic_manager.catalyst_system
                
                # Lógica simples de drop por nome
                item = "salamander_tail" # Default
                name_lower = entity.name.lower()
                
                if "water" in name_lower: item = "water_sphere"
                elif "void" in name_lower: item = "void_dust"
                elif "summon" in name_lower: item = "summoning_core"
                
                sys.give_catalyst(killer.id, item, 1)
                # Opcional: Feedback visual ao jogador seria ideal aqui
                logger.info(f"LOOT: {killer.name} obteve catalisador {item}")
            # ==========================================

        if isinstance(entity, NPCInstance):
            self.world.kill_npc(entity.uid)

    def _get_entity(self, entity_id: str):
        if isinstance(entity_id, int): return self.world.get_player(str(entity_id)) # Assume conversão segura
        if isinstance(entity_id, str) and entity_id.isdigit(): return self.world.get_player(entity_id)
        return self.world.get_npc(entity_id)

    def _get_id(self, entity):
        if isinstance(entity, Character): return str(entity.id)
        return entity.uid

    def _is_alive(self, entity) -> bool:
        if isinstance(entity, Character): return entity.hp.current > 0
        return entity.is_alive()

    def _get_equipped_weapon(self, entity) -> Optional[ItemTemplate]:
        if isinstance(entity, Character):
            item_uid = entity.equipment.get("main_hand")
            if item_uid:
                instance = self.world.active_items.get(item_uid)
                if instance:
                    return self.world.factory._item_templates.get(instance.template_vnum)
        return None

    def _get_damage_verb(self, dmg_type: str, amount: int) -> str:
        if amount < 5: return "arranha"
        if amount > 20: return "DESTROÇA"
        return "atinge"

    def _broadcast_to_room(self, room_vnum: int, message: str):
        logger.info(f"[ROOM {room_vnum}] {message.strip()}")