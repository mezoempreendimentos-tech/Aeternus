import random
from aeternus.game.world import world

class CombatEngine:
    def __init__(self):
        pass

    async def perform_round(self, attacker, defender):
        """
        Calcula um round de combate.
        Agora usa o sistema 'High Roll' (D&D Style).
        Quanto maior o dado, melhor.
        """
        if not attacker or not defender: return
        
        # 1. Coleta Atributos
        att_dex = getattr(attacker, 'dexterity', 10)
        att_str = getattr(attacker, 'strength', 10)
        att_lvl = getattr(attacker, 'level', 1)
        
        def_dex = getattr(defender, 'dexterity', 10)
        def_lvl = getattr(defender, 'level', 1)
        
        # 2. A Matemática da Guerra
        # Target Number (Dificuldade) = 50 + Defesa - Ataque
        # Se o atacante for muito bom, a dificuldade cai.
        attack_bonus = (att_dex * 2) + (att_lvl * 2)
        defense_bonus = (def_dex * 2) + (def_lvl * 2)
        
        difficulty = 50 + defense_bonus - attack_bonus
        # Mantém a dificuldade sanável (entre 5 e 95)
        difficulty = max(5, min(95, difficulty))
        
        # 3. A Rolagem do Destino (d100)
        roll = random.randint(1, 100)
        
        # --- CENÁRIOS ---
        
        # A) SUCESSO ABSOLUTO (Crítico - Top 5%)
        if roll >= 96:
            await self.apply_damage(attacker, defender, att_str, multiplier=2.0, is_crit=True)
            
        # B) FALHA CATASTRÓFICA (Fumble - Bot 5%)
        elif roll <= 5:
            await self.handle_fumble(attacker, defender)
            
        # C) ACERTO NORMAL (Rolagem >= Dificuldade)
        elif roll >= difficulty:
            await self.apply_damage(attacker, defender, att_str, multiplier=1.0, is_crit=False)
            
        # D) ERRO NORMAL
        else:
            await self.send_combat_msg(attacker, defender, "miss")

    async def apply_damage(self, attacker, defender, strength, multiplier=1.0, is_crit=False):
        """Calcula e aplica o dano."""
        # Dano Base
        base_dmg = int(strength / 2) + random.randint(1, 6)
        
        # Aplica Multiplicador (Crítico)
        final_dmg = int(base_dmg * multiplier)
        if final_dmg < 1: final_dmg = 1
        
        defender.take_damage(final_dmg)
        
        msg_type = "crit" if is_crit else "hit"
        await self.send_combat_msg(attacker, defender, msg_type, final_dmg)
        
        if not defender.is_alive():
            await self.handle_death(attacker, defender)

    async def handle_fumble(self, attacker, defender):
        """
        Quando o ataque é tão ruim que atrapalha o atacante.
        """
        # Penalidade: Perde um pouco de Stamina ou toma 1 de dano moral
        attacker.stamina = max(0, attacker.stamina - 10)
        
        await self.send_combat_msg(attacker, defender, "fumble")

    async def send_combat_msg(self, att, deff, type, dmg=0):
        """Envia mensagens narrativas e viscerais."""
        
        if type == "crit":
            to_att = f"\033[1;33m*** GOLPE DE MESTRE! ***\033[0m\n\033[1;32mVocê atinge um ponto vital de {deff.name}! \033[1;31m[{dmg} DANO CRÍTICO]\033[0m"
            to_def = f"\033[1;31m*** DOR AGONIZANTE! ***\n{att.name} esmaga seus ossos com um golpe perfeito! [{dmg} DANO CRÍTICO]\033[0m"
            to_room = f"\033[1;33m{att.name} desfere um golpe BRUTAL e CRÍTICO em {deff.name}!\033[0m"

        elif type == "hit":
            to_att = f"\033[1;32mVocê acerta {deff.name}. \033[1;31m[{dmg}]\033[0m"
            to_def = f"\033[1;31m{att.name} acerta você! [{dmg}]\033[0m"
            to_room = f"{att.name} acerta {deff.name} com força."

        elif type == "miss":
            to_att = f"\033[0;33mVocê tenta acertar {deff.name}, mas ele esquiva.\033[0m"
            to_def = f"\033[1;32mVocê se esquiva agilmente do ataque de {att.name}.\033[0m"
            to_room = f"{att.name} ataca o ar, errando {deff.name}."

        elif type == "fumble":
            to_att = f"\033[1;35m*** DESASTRE! ***\033[0m\n\033[0;31mVocê tropeça e quase cai! Seu ataque foi patético.\033[0m"
            to_def = f"\033[1;36m{att.name} se atrapalha todo e quase cai sozinho. Que amador!\033[0m"
            to_room = f"\033[1;35m{att.name} tropeça nos próprios pés e faz um ataque ridículo contra {deff.name}.\033[0m"

        # Envio Seguro
        if hasattr(att, 'connection') and att.connection:
            await att.connection.send(to_att)
        if hasattr(deff, 'connection') and deff.connection:
            await deff.connection.send(to_def)
            
        # Sala
        if att.room:
            for p in att.room.people:
                if p != att and p != deff and hasattr(p, 'connection') and p.connection:
                    await p.connection.send(to_room)

    async def handle_death(self, killer, victim):
        # Mensagens Finais
        if hasattr(killer, 'connection') and killer.connection:
            xp = getattr(victim, 'level', 1) * 100
            await killer.connection.send(f"\n\033[1;31mVOCÊ ESTRAÇALHOU {victim.name}!\033[0m")
            await killer.connection.send(f"\033[1;36mVocê absorve {xp} de experiência vital.\033[0m\n")
            
        if hasattr(victim, 'connection') and victim.connection:
            await victim.connection.send("\n\033[1;30mA luz se apaga. O frio do túmulo lhe abraça.\033[0m\n")

        await self.stop_combat(killer, victim)
        
        # Cadáver
        corpse = world.create_item("3001") or world.create_item("1")
        if corpse:
            corpse.name = f"o cadáver destroçado de {victim.name}"
            corpse.description = f"O corpo sem vida de {victim.name} jaz aqui, sangrando."
            corpse.keywords.extend(["cadáver", "corpo", "carne"])
            
            corpse.contents = list(victim.inventory)
            victim.inventory = []
            
            if victim.room:
                victim.room.contents.append(corpse)
                if victim in victim.room.people:
                    victim.room.people.remove(victim)

        # Destino
        if hasattr(victim, 'connection'):
            limbo = world.get_room("010103003001") or world.get_room("0")
            if limbo:
                victim.room = limbo
                limbo.people.append(victim)
                victim.hp = 10
                await victim.connection.send("Você acorda no Templo, a alma marcada pela derrota.")

    async def stop_combat(self, char1, char2):
        if char1.fighting == char2: char1.fighting = None
        if char2.fighting == char1: char2.fighting = None

combat_engine = CombatEngine()