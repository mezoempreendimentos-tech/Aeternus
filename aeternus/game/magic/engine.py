import random
from aeternus.game.combat.combat_engine import combat_engine

class MagicEngine:
    def roll_damage(self, min_val, max_val):
        return random.randint(min_val, max_val)

    async def initiate_cast(self, caster, spell, target):
        """
        Começa o ritual. Verifica cooldowns e mana.
        """
        # 1. Validações Básicas
        if caster.position == "sleeping":
            await self.send_msg(caster, "Você está dormindo.")
            return

        # 2. Verifica Cooldown
        if spell.id in caster.cooldowns:
            ticks_left = caster.cooldowns[spell.id]
            await self.send_msg(caster, f"Você ainda não recuperou a energia para essa magia ({ticks_left} ticks).")
            return

        # 3. Verifica Mana
        if caster.mana < spell.mana:
            await self.send_msg(caster, "Você não tem mana suficiente.")
            return

        # 4. Inicia Concentração
        await self.send_msg(caster, f"\033[1;36mVocê começa a entoar as palavras de '{spell.name}'...\033[0m")
        
        # Avisa a sala
        if caster.room:
            for p in caster.room.people:
                if p != caster and hasattr(p, 'connection'):
                    await self.send_msg(p, f"\033[0;36m{caster.name} começa a gesticular e entoar mantras arcanos.\033[0m")

        # Define o Estado
        caster.casting = {
            'spell': spell,
            'target': target,
            'timer': spell.cast_time
        }

    async def finalize_cast(self, caster):
        """
        Chamado pelo GameLoop quando o timer chega a 0.
        """
        if not caster.casting: return
        
        spell = caster.casting['spell']
        target = caster.casting['target']
        
        # Limpa estado imediatamente
        caster.casting = None

        # Revalidações (O alvo ainda está aqui? Tenho mana?)
        if caster.mana < spell.mana:
            await self.send_msg(caster, "Sua mana falhou no último segundo!")
            return
            
        if target and target.room != caster.room:
            await self.send_msg(caster, "Seu alvo desapareceu!")
            return

        # Consome Mana e Aplica Cooldown
        caster.mana -= spell.mana
        caster.cooldowns[spell.id] = spell.cooldown

        # Rolagem de Resultado
        roll = random.randint(1, 100)
        outcome = "normal"
        if roll <= 5: outcome = "backfire"
        elif roll >= 96: outcome = "crit"

        # Executa o Efeito
        await spell.func(caster, target, self, outcome)

    # --- MÉTODOS DE EFEITO ---
    async def apply_spell_damage(self, caster, target, damage, messages):
        msg_cast, msg_targ, msg_room = messages
        await self.broadcast(caster, target, msg_cast, msg_targ, msg_room)
        
        target.take_damage(damage)
        if hasattr(caster, 'connection'):
            await caster.connection.send(f"\033[1;30m[Dano Mágico: {damage}]\033[0m")

        if not caster.fighting and target.is_alive() and caster != target:
            caster.fighting = target
            target.fighting = caster
            
        if not target.is_alive():
            await combat_engine.handle_death(caster, target)

    async def apply_spell_self_damage(self, caster, damage, messages):
        msg_cast, msg_room = messages
        if hasattr(caster, 'connection'): await caster.connection.send(msg_cast)
        if caster.room:
            for p in caster.room.people:
                if p != caster and hasattr(p, 'connection'): await p.connection.send(msg_room)

        caster.take_damage(damage)
        await caster.connection.send(f"\033[1;30m[Backfire: {damage}]\033[0m")
        
        if not caster.is_alive():
            await combat_engine.handle_death(caster, caster)

    async def apply_spell_heal(self, caster, target, amount, messages):
        msg_cast, msg_targ, msg_room = messages
        old_hp = target.hp
        target.hp = min(target.max_hp, target.hp + amount)
        real_heal = target.hp - old_hp
        
        await self.broadcast(caster, target, msg_cast, msg_targ, msg_room)
        if hasattr(caster, 'connection'):
            await caster.connection.send(f"\033[1;30m[Cura: {real_heal}]\033[0m")

    async def broadcast(self, caster, target, m_cast, m_targ, m_room):
        if hasattr(caster, 'connection') and caster.connection:
            await caster.connection.send(m_cast)
        if target and target != caster and hasattr(target, 'connection') and target.connection:
            await target.connection.send(m_targ)
        
        if caster.room:
            for p in caster.room.people:
                if p != caster and p != target and hasattr(p, 'connection') and p.connection:
                    await p.connection.send(m_room)

    async def send_msg(self, char, msg):
        if hasattr(char, 'connection') and char.connection:
            await char.connection.send(msg)

magic_engine = MagicEngine()