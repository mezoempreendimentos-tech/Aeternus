# backend/game/commands/core.py
from backend.game.utils.vnum import VNum

# --- MAPEAMENTO VISUAL ---
DIRECTION_DISPLAY = {
    "north": "Norte", "south": "Sul", "east": "Leste", "west": "Oeste",
    "northeast": "Nordeste", "northwest": "Noroeste",
    "southeast": "Sudeste", "southwest": "Sudoeste",
    "up": "Cima", "down": "Baixo"
}

# --- COMANDOS DE INFORMAÇÃO ---
def cmd_look(ctx) -> str:
    room = ctx.world.get_room(ctx.player.location_vnum)
    if not room: return "Você está no Limbo."

    buffer = []
    buffer.append(f"== {room.title} ==")
    buffer.append(room.get_description(False)) 

    # Entidades
    for uid in room.npcs_here:
        npc = ctx.world.get_npc(uid)
        if npc:
            buffer.append(f"> {npc.full_name} está aqui.")

    for uid in room.items_here:
        item = ctx.world.active_items.get(uid)
        if item:
            t = ctx.world.factory._item_templates.get(item.template_vnum)
            name = item.custom_name or (t.name if t else "Item ???")
            buffer.append(f"- {name} está no chão.")

    for pid in room.players_here:
        if pid != ctx.player.id:
            p = ctx.world.get_player(pid)
            if p: buffer.append(f"* {p.name} está aqui.")
            
    # Saídas
    exits = [d for d in room.exits.keys()]
    buffer.append(f"[Saídas: {' '.join(exits) if exits else 'Nenhuma'}]")

    return "\n".join(buffer)

def cmd_inventory(ctx) -> str:
    if not ctx.player.inventory: return "Mochila vazia."
    
    buffer = ["== Mochila =="]
    for uid in ctx.player.inventory:
        item = ctx.world.get_item(uid)
        if item:
            tmpl = ctx.world.factory._item_templates.get(item.template_vnum)
            name = item.custom_name or (tmpl.name if tmpl else "???")
            buffer.append(f"- {name}")
    return "\n".join(buffer)

def cmd_equipment(ctx) -> str:
    buffer = ["== Equipamento =="]
    for slot, uid in ctx.player.equipment.items():
        val = "[Item]" if uid else "(Vazio)"
        buffer.append(f"{slot.capitalize()}: {val}")
    return "\n".join(buffer)

# --- COMANDOS DE INVENTÁRIO (NOVO) ---

def cmd_get(ctx) -> str:
    """pegar <item>"""
    if not ctx.args: return "Pegar o quê?"
    target_name = ctx.raw_args.lower()
    
    room = ctx.world.get_room(ctx.player.location_vnum)
    
    # Busca item na sala pelo nome (Fuzzy Search)
    target_uid = None
    target_item = None
    
    for uid in room.items_here:
        item = ctx.world.get_item(uid)
        if not item: continue
        tmpl = ctx.world.factory._item_templates.get(item.template_vnum)
        name = (item.custom_name or tmpl.name).lower()
        
        if target_name in name:
            target_uid = uid
            target_item = name
            break
            
    if not target_uid:
        return "Não vejo isso aqui."
        
    if ctx.world.pick_up_item(ctx.player.id, target_uid):
        return f"Você pegou {target_item}."
    return "Você não consegue pegar isso."

def cmd_drop(ctx) -> str:
    """largar <item>"""
    if not ctx.args: return "Largar o quê?"
    target_name = ctx.raw_args.lower()
    
    # Busca no inventário
    target_uid = None
    target_item = None
    
    for uid in ctx.player.inventory:
        item = ctx.world.get_item(uid)
        if not item: continue
        tmpl = ctx.world.factory._item_templates.get(item.template_vnum)
        name = (item.custom_name or tmpl.name).lower()
        
        if target_name in name:
            target_uid = uid
            target_item = name
            break
            
    if not target_uid:
        return "Você não tem isso."
        
    if ctx.world.drop_item(ctx.player.id, target_uid):
        return f"Você largou {target_item}."
    return "Você não consegue largar isso."

# --- MOVIMENTO E COMBATE ---
def cmd_move(ctx, direction: str) -> str:
    room = ctx.world.get_room(ctx.player.location_vnum)
    if not room: return "Lugar nenhum."
    exit_info = room.exits.get(direction)
    if not exit_info: return "Não há saída nessa direção."
    if ctx.world.move_character(ctx.player.id, exit_info.target_vnum):
        return cmd_look(ctx)
    return "Algo bloqueia seu caminho."

async def cmd_kill(ctx) -> str:
    if not ctx.args: return "Matar quem?"
    target_name = ctx.raw_args.lower()
    room = ctx.world.get_room(ctx.player.location_vnum)
    target = None
    for uid in room.npcs_here:
        npc = ctx.world.get_npc(uid)
        if npc and target_name in npc.name.lower():
            target = npc
            break
    if not target: return "Não vejo ninguém com esse nome aqui."
    await ctx.combat.start_combat(ctx.player, target)
    return f"Você assume postura de combate contra {target.name}!"