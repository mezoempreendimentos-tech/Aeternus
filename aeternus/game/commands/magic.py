from aeternus.game.magic.spellbook import SPELLS
from aeternus.game.magic.engine import magic_engine

async def do_cast(connection, args):
    if not args:
        await connection.send("Conjurar o quê?")
        return

    clean_args = [a.replace("'", "").replace('"', "") for a in args]
    full_input = " ".join(clean_args).lower()
    
    spell = None
    best_match_len = 0
    
    for spell_name, spell_obj in SPELLS.items():
        if full_input.startswith(spell_name):
            if len(spell_name) > best_match_len:
                spell = spell_obj
                best_match_len = len(spell_name)
    
    if not spell:
        known = ", ".join(list(SPELLS.keys())[:10])
        await connection.send(f"Magia desconhecida. (Tente: {known}...)")
        return

    # Auto-Learn para Debug
    player = connection.player
    if spell.id not in player.spells_known:
        player.spells_known.add(spell.id)
        await connection.send(f"\033[1;35m(DEBUG) Magia aprendida: {spell.name}\033[0m")

    target_part = full_input[best_match_len:].strip()
    caster = connection.player
    target = None

    if not target_part:
        if spell.target_type == "offensive":
            if caster.fighting: target = caster.fighting
            else:
                await connection.send("Conjurar em quem?")
                return
        else:
            target = caster
    else:
        for char in caster.room.people:
            if target_part in char.name.lower(): target = char; break
            if hasattr(char, 'keywords') and any(k.startswith(target_part) for k in char.keywords):
                target = char; break
    
    if not target:
        await connection.send("Alvo não encontrado.")
        return

    # CHAMA O NOVO MÉTODO
    await magic_engine.initiate_cast(caster, spell, target)