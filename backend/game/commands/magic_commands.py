async def cmd_pesquisar(ctx) -> str:
    """Entra no modo de laboratório."""
    return ctx.world.magic_manager.catalyst_system.start_research_session(ctx.player)

async def cmd_conjurar(ctx) -> str:
    """Uso: conjurar <id> [alvo]"""
    if not ctx.args: return "Conjurar qual magia (ID)?"
    try:
        vnum = int(ctx.args[0])
        target = " ".join(ctx.args[1:]) if len(ctx.args) > 1 else ""
        return await ctx.world.magic_manager.cast_spell(ctx.player, vnum, target)
    except: return "ID inválido."

async def cmd_catalisadores(ctx) -> str:
    cats = ctx.world.magic_manager.catalyst_system.player_catalysts.get(ctx.player.id, {})
    if not cats: return "Bolsa de reagentes vazia."
    return "=== BOLSAS ===\n" + "\n".join([f"- {k}: {v}" for k,v in cats.items()])

def register_magic_commands(handler):
    handler.register("pesquisar", cmd_pesquisar, ["research", "lab"])
    handler.register("conjurar", cmd_conjurar, ["cast", "c"])
    handler.register("catalisadores", cmd_catalisadores, ["reagentes"])