import asyncio
import traceback
from aeternus.game.world import world
from aeternus.core.config import settings
from aeternus.game.combat.combat_engine import combat_engine
from aeternus.game.magic.engine import magic_engine

class GameLoop:
    def __init__(self):
        self.running = False
        self.tick_count = 0
        self.time_tick = 0 
        self.zone_timer = 0 # <--- A LINHA PERDIDA (Restaurada)

    async def start(self):
        self.running = True
        print("⏳ [GAME LOOP] O Cronos despertou.")
        
        while self.running:
            try:
                self.tick_count += 1
                self.time_tick += 1
                
                # 1. Tick de Combate e Magia (A cada 3 segundos)
                if self.tick_count % 3 == 0:
                    await self.process_magic_ticks()
                    await self.process_combat()
                
                # 2. Regeneração (10s)
                if self.tick_count % 10 == 0:
                    await self.process_regen()

                # 3. Tempo e Respawn (60s)
                if self.tick_count >= 60:
                    await self.process_world_tick()
                    self.tick_count = 0
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"💥 [CRASH NO LOOP]: {e}")
                traceback.print_exc()
                await asyncio.sleep(1)

    async def process_magic_ticks(self):
        """
        Gere o tempo de conjuração e cooldowns.
        """
        for player in world.active_players:
            # 1. Decrementa Cooldowns
            toremove = []
            for spell_id in player.cooldowns:
                player.cooldowns[spell_id] -= 1
                if player.cooldowns[spell_id] <= 0:
                    toremove.append(spell_id)
            
            for sid in toremove:
                del player.cooldowns[sid]

            # 2. Processa Casting
            if player.casting:
                player.casting['timer'] -= 1
                if player.casting['timer'] <= 0:
                    await magic_engine.finalize_cast(player)

    async def process_combat(self):
        active_fighters = [p for p in world.active_players if p.fighting]
        if not active_fighters: return
        processed = set()
        for char in active_fighters:
            if char in processed: continue
            target = char.fighting
            if not target: 
                char.fighting = None; continue
            if target.fighting == char: processed.add(target)
            
            if char.room and target.room and char.room == target.room:
                await combat_engine.perform_round(char, target)
                if target.is_alive() and target.fighting == char:
                    await combat_engine.perform_round(target, char)
            else:
                if hasattr(char, 'connection') and char.connection:
                    await char.connection.send("Alvo perdido.")
                char.fighting = None; target.fighting = None

    async def process_regen(self):
        for p in world.active_players:
            if p.hp < p.max_hp or p.mana < p.max_mana or p.stamina < p.max_stamina:
                p.regenerate()
        
        active_rooms = set(p.room for p in world.active_players if p.room)
        for room in active_rooms:
            for mob in room.people:
                if hasattr(mob, 'connection'): continue
                if mob.hp < mob.max_hp:
                    mob.regenerate()

    async def process_world_tick(self):
        # 1. Avança o Tempo
        msg_time = world.advance_time()
        if msg_time:
            for p in world.active_players:
                if p.connection: await p.connection.send(msg_time)

        # 2. Respawn das Zonas (Usa o zone_timer agora inicializado)
        self.zone_timer += 1
        if self.zone_timer >= settings.DEFAULT_RESPAWN_TIME:
            # print(f"⚡ [GAME LOOP] Zone Reset...")
            try: world.populate_world()
            except: pass
            self.zone_timer = 0

gameloop = GameLoop()