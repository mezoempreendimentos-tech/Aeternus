async def cmd_catalisadores(ctx) -> str:
    """Lista reagentes."""
    sys = ctx.world.magic_manager.catalyst_system
    cats = sys.get_player_catalysts(ctx.player.id)
    if not cats: return "Sua bolsa de reagentes está vazia."
    
    out = ["=== BOLSA DE REAGENTES ==="]
    for cid, amt in cats.items():
        tmpl = sys.catalyst_templates.get(cid)
        name = tmpl.name if tmpl else cid
        out.append(f"- {name} x{amt}")
    return "\n".join(out)

def register_catalyst_commands(handler):
    handler.register("catalisadores", cmd_catalisadores, ["reagentes", "cats"])