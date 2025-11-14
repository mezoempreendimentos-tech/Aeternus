# ==============================================================================
# ESTRUTURA DA MAGIA
# ==============================================================================
class Spell:
    def __init__(self, id, name, mana, target_type, school, cast_time, cooldown, func):
        self.id = id
        self.name = name
        self.mana = mana
        self.target_type = target_type # "offensive", "defensive"
        self.school = school           # "Evocation", "Restoration", etc
        self.cast_time = cast_time     # Ticks para conjurar (1 tick = 3s)
        self.cooldown = cooldown       # Ticks de espera após usar
        self.func = func 

# Dicionário Global
SPELLS = {}

def register_spell(id, name, mana, type, school, cast_time, cooldown, func):
    s = Spell(id, name, mana, type, school, cast_time, cooldown, func)
    SPELLS[id] = s
    SPELLS[name.lower()] = s

# ==============================================================================
# IMPLEMENTAÇÃO DAS MAGIAS
# ==============================================================================

# 1. Míssil Mágico (Evocação)
async def cast_magic_missile(caster, target, engine, outcome):
    int_bonus = getattr(caster, 'intelligence', 10)
    min_dmg = 5 + (int_bonus // 2)
    max_dmg = 10 + int_bonus
    
    if outcome == "crit":
        damage = int(engine.roll_damage(min_dmg, max_dmg) * 2)
        msg_cast = f"\033[1;36m*** PODER ARCANO! ***\nUm Míssil de Energia Pura explode de suas mãos contra {target.name}!\033[0m"
        msg_targ = f"\033[1;31m*** IMPACTO! ***\nUm Míssil Mágico CRÍTICO perfura sua defesa!\033[0m"
        msg_room = f"\033[1;36mUm Míssil Mágico cegante atinge {target.name} com violência!\033[0m"
        await engine.apply_spell_damage(caster, target, damage, (msg_cast, msg_targ, msg_room))

    elif outcome == "backfire":
        damage = int(engine.roll_damage(min_dmg, max_dmg) / 2)
        msg_cast = f"\033[1;35m*** INSTABILIDADE! ***\nA energia colapsa antes de sair!\033[0m"
        msg_room = f"\033[1;35mO feitiço de {caster.name} falha e explode em seu rosto!\033[0m"
        await engine.apply_spell_self_damage(caster, damage, (msg_cast, msg_room))

    else:
        damage = engine.roll_damage(min_dmg, max_dmg)
        msg_cast = f"\033[1;36mVocê dispara um dardo de energia em {target.name}!\033[0m"
        msg_targ = f"\033[1;31m{caster.name} atinge você com um dardo de energia!\033[0m"
        msg_room = f"\033[0;36mUm dardo de energia de {caster.name} atinge {target.name}.\033[0m"
        await engine.apply_spell_damage(caster, target, damage, (msg_cast, msg_targ, msg_room))

# 2. Curar Ferimentos Leves (Restauração)
async def cast_cure_light(caster, target, engine, outcome):
    wis_bonus = getattr(caster, 'wisdom', 10)
    base = 10 + wis_bonus
    
    if outcome == "crit":
        amount = int(base * 2)
        msg_cast = f"\033[1;33m*** BÊNÇÃO DIVINA! ***\nLuz sagrada inunda suas mãos!\033[0m"
        msg_targ = f"\033[1;33mVocê sente o toque direto dos deuses! Suas feridas somem.\033[0m"
        msg_room = f"\033[1;33mUma luz ofuscante desce sobre {target.name}!\033[0m"
        await engine.apply_spell_heal(caster, target, amount, (msg_cast, msg_targ, msg_room))

    elif outcome == "backfire":
        amount = int(base / 2)
        msg_cast = f"\033[1;35m*** CORRUPÇÃO! ***\nVocê canaliza energia necrótica por engano!\033[0m"
        msg_targ = f"\033[1;31mO feitiço de cura de {caster.name} queima sua pele!\033[0m"
        msg_room = f"\033[1;35mO feitiço de {caster.name} torna-se negro e fere {target.name}!\033[0m"
        await engine.apply_spell_damage(caster, target, amount, (msg_cast, msg_targ, msg_room))

    else:
        amount = base
        msg_cast = f"\033[1;33mUma luz suave fecha as feridas de {target.name}.\033[0m"
        msg_targ = f"\033[1;33mVocê se sente melhor com a cura de {caster.name}.\033[0m"
        msg_room = f"\033[0;33mUma aura dourada envolve {target.name}.\033[0m"
        await engine.apply_spell_heal(caster, target, amount, (msg_cast, msg_targ, msg_room))

# ==============================================================================
# REGISTRO (ID, Nome, Mana, Tipo, Escola, CastTime, Cooldown, Func)
# ==============================================================================
# Magic Missile: 1 Tick para castar, 3 Ticks de Cooldown
register_spell("magic missile", "Míssil Mágico", 15, "offensive", "Evocação", 1, 3, cast_magic_missile)
# Cure Light: 1 Tick para castar, 1 Tick de Cooldown
register_spell("cure light", "Curar Ferimentos Leves", 10, "defensive", "Restauração", 1, 1, cast_cure_light)

# Alias
register_spell("missil magico", "Míssil Mágico", 15, "offensive", "Evocação", 1, 3, cast_magic_missile)
register_spell("curar leve", "Curar Ferimentos Leves", 10, "defensive", "Restauração", 1, 1, cast_cure_light)