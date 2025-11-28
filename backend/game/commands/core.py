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
    """O ato de observar o mundo."""
    room = ctx.world.get_room(ctx.player.location_vnum)
    if not room: return "Você está no Limbo."

    buffer = []
    buffer.append(f"== {room.title} ==")
    buffer.append(room.get_description(False)) # Futuro: checar dia/noite

    # Sensorial
    perc = ctx.player.attributes["perception"].total
    if perc >= 12:
        if room.sensory.visual: buffer.append(f"[Visão] {room.sensory.visual}")
        if room.sensory.auditory: buffer.append(f"[Som] {room.sensory.auditory}")

    buffer.append("") 

    # Saídas
    exits = []
    for d, info in room.exits.items():
        if not info.is_hidden:
            exits.append(DIRECTION_DISPLAY.get(d, d.capitalize()))
    buffer.append(f"[Saídas: {' '.join(exits) if exits else 'Nenhuma'}]")

    # Entidades
    for uid in room.npcs_here:
        npc = ctx.world.get_npc(uid)
        if npc:
            status = " [ALPHA]" if npc.has_flag("ZONE_ALPHA") else ""
            if npc.current_hp < npc.total_hp: status += " (Ferido)"
            buffer.append(f"> {npc.full_name}{status} está aqui.")

    for uid in room.items_here:
        item = ctx.world.active_items.get(uid)
        if item:
            # Nome vem do template se não tiver custom
            t = ctx.world.factory._item_templates.get(item.template_vnum)
            name = item.custom_name or (t.name if t else "Item ???")
            buffer.append(f"- {name} está no chão.")

    for pid in room.players_here:
        if pid != ctx.player.id:
            p = ctx.world.get_player(pid)
            if p: buffer.append(f"* {p.name} está aqui.")

    return "\n".join(buffer)

def cmd_inventory(ctx) -> str:
    if not ctx.player.inventory: return "Mochila vazia."
    return f"Você carrega {len(ctx.player.inventory)} itens."

def cmd_equipment(ctx) -> str:
    buffer = ["== Equipamento =="]
    for slot, uid in ctx.player.equipment.items():
        val = "[Item]" if uid else "(Vazio)"
        buffer.append(f"{slot.capitalize()}: {val}")
    return "\n".join(buffer)

# --- COMANDOS DE MOVIMENTO ---

def cmd_move(ctx, direction: str) -> str:
    room = ctx.world.get_room(ctx.player.location_vnum)
    if not room: return "Lugar nenhum."

    exit_info = room.exits.get(direction)
    if not exit_info: return "Não há saída nessa direção."
    if exit_info.is_locked: return "Está trancado."

    if ctx.world.move_character(ctx.player.id, exit_info.target_vnum):
        return cmd_look(ctx)
    return "Algo bloqueia seu caminho."

# --- COMANDOS DE COMBATE ---

async def cmd_kill(ctx) -> str:
    """
    Inicia combate.
    Sintaxe: matar <nome>
    """
    if not ctx.args:
        return "Matar quem? (Uso: matar <nome>)"
    
    target_name = ctx.raw_args.lower()
    room = ctx.world.get_room(ctx.player.location_vnum)
    
    # Busca Alvo na Sala (Fuzzy match simples)
    target = None
    
    # 1. Procura em NPCs
    for uid in room.npcs_here:
        npc = ctx.world.get_npc(uid)
        if npc and target_name in npc.name.lower():
            target = npc
            break
            
    # 2. Procura em Players (PvP - Opcional)
    if not target:
        for pid in room.players_here:
            if pid == ctx.player.id: continue
            p = ctx.world.get_player(pid)
            if p and target_name in p.name.lower():
                target = p
                break
    
    if not target:
        return "Não vejo ninguém com esse nome aqui para matar."
    
    # Inicia a Sessão de Combate
    # O CombatManager vai lidar com a lógica de turnos a partir de agora
    await ctx.combat.start_combat(ctx.player, target)
    
    return f"Você assume postura de combate contra {target.name}!"