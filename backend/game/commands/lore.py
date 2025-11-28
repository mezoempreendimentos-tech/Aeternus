# backend/game/commands/lore.py
"""
Comandos para interagir com o Grimório Vivo.
"""

from typing import List
import random

async def cmd_lendas(ctx) -> str:
    """
    Mostra lendas conhecidas.
    Uso: lendas [sobre <jogador>] [zona]
    """
    grimoire = ctx.world.grimoire  # Assumindo que foi adicionado ao WorldManager
    
    if not grimoire or not grimoire.legends:
        return "O mundo ainda é jovem. Nenhuma lenda foi forjada."
    
    # Filtros
    if ctx.args and ctx.args[0].lower() == "sobre" and len(ctx.args) > 1:
        target_name = " ".join(ctx.args[1:])
        legends = grimoire.get_legends_about_player(target_name)
        
        if not legends:
            return f"Nenhuma lenda existe sobre {target_name}... ainda."
        
        buffer = [f"=== LENDAS SOBRE {target_name.upper()} ===\n"]
        for legend in sorted(legends, key=lambda l: l.epic_score, reverse=True):
            epic_bar = "★" * (legend.epic_score // 20)
            buffer.append(
                f"{epic_bar} {legend.title}\n"
                f"   Categoria: {legend.category.capitalize()} | "
                f"Épica: {legend.epic_score}/100 | "
                f"Conhecida por {len(legend.believers)} almas"
            )
        
        return "\n".join(buffer)
    
    elif ctx.args and ctx.args[0].lower() == "zona":
        # Lendas da zona atual
        room = ctx.world.get_room(ctx.player.location_vnum)
        zone_id, _ = ctx.world.factory._parse_vnum(room.vnum)
        
        legends = grimoire.get_zone_legends(zone_id)
        
        if not legends:
            return "Esta região ainda não tem lendas próprias."
        
        buffer = [f"=== LENDAS DESTA REGIÃO ===\n"]
        for legend in legends[:5]:  # Top 5
            buffer.append(f"• {legend.title} ({legend.category})")
        
        return "\n".join(buffer)
    
    else:
        # Lista geral (top 10 mais épicas)
        top_legends = sorted(
            grimoire.legends.values(), 
            key=lambda l: l.epic_score, 
            reverse=True
        )[:10]
        
        buffer = ["=== O GRIMÓRIO DAS GRANDES LENDAS ===\n"]
        
        for i, legend in enumerate(top_legends, 1):
            spread = f"({legend.spread_count} vezes contada)" if legend.spread_count > 0 else ""
            buffer.append(f"{i}. {legend.title} {spread}")
            buffer.append(f"   Protagonista: {legend.protagonist} | Épica: {legend.epic_score}/100\n")
        
        buffer.append("\nUse 'lendas sobre <nome>' para ver lendas de alguém.")
        buffer.append("Use 'lendas zona' para ver histórias locais.")
        
        return "\n".join(buffer)


async def cmd_ouvir(ctx) -> str:
    """
    Ouve uma lenda de um NPC.
    Uso: ouvir [npc] [número da lenda]
    """
    grimoire = ctx.world.grimoire
    
    if not ctx.args:
        return (
            "Uso: ouvir <npc>\n"
            "Exemplo: ouvir rato\n"
            "O NPC te contará uma história que conhece."
        )
    
    # Busca NPC na sala
    target_name = ctx.raw_args.lower()
    room = ctx.world.get_room(ctx.player.location_vnum)
    
    target_npc = None
    for npc_uid in room.npcs_here:
        npc = ctx.world.get_npc(npc_uid)
        if npc and target_name in npc.name.lower():
            target_npc = npc
            break
    
    if not target_npc:
        return "Não vejo esse contador de histórias por aqui."
    
    # Verifica se o NPC conhece alguma lenda
    memory = grimoire.npc_memories.get(target_npc.uid)
    
    if not memory or not memory.known_legends:
        return f"{target_npc.name} olha para você sem entender. Talvez não saiba histórias."
    
    # Escolhe lenda aleatória que o NPC conhece
    legend_id = random.choice(memory.known_legends)
    
    # NPC conta a história
    narrative = await grimoire.npc_tell_legend(target_npc.uid, legend_id)
    
    if not narrative:
        return f"{target_npc.name} começa a falar mas se perde no meio da história."
    
    return f"\n{narrative}\n"


async def cmd_reputacao(ctx) -> str:
    """
    Mostra sua reputação baseada em lendas.
    Uso: reputacao [jogador]
    """
    grimoire = ctx.world.grimoire
    
    target_name = " ".join(ctx.args) if ctx.args else ctx.player.name
    
    legends = grimoire.get_legends_about_player(target_name)
    
    if not legends:
        if target_name.lower() == ctx.player.name.lower():
            return (
                "Sua história ainda está sendo escrita.\n"
                "Feitos épicos forjarão sua lenda."
            )
        else:
            return f"{target_name} ainda não é conhecido nas canções."
    
    # Calcula estatísticas
    total_epic = sum(l.epic_score for l in legends)
    avg_epic = total_epic // len(legends)
    total_spread = sum(l.spread_count for l in legends)
    
    # Classifica reputação
    if avg_epic >= 80:
        reputation_tier = "LENDÁRIO"
        emoji = "👑"
    elif avg_epic >= 60:
        reputation_tier = "HEROICO"
        emoji = "⚔️"
    elif avg_epic >= 40:
        reputation_tier = "CONHECIDO"
        emoji = "🗡️"
    else:
        reputation_tier = "INICIANTE"
        emoji = "🌱"
    
    # Categorias de lendas
    categories = {}
    for legend in legends:
        categories[legend.category] = categories.get(legend.category, 0) + 1
    
    buffer = [
        f"=== REPUTAÇÃO DE {target_name.upper()} ===",
        f"{emoji} Status: {reputation_tier}",
        f"Lendas Registradas: {len(legends)}",
        f"Épica Média: {avg_epic}/100",
        f"Vezes Contada: {total_spread}",
        "",
        "Tipos de Lendas:"
    ]
    
    for cat, count in categories.items():
        buffer.append(f"  • {cat.capitalize()}: {count}")
    
    buffer.append("\nLendas Mais Épicas:")
    top_3 = sorted(legends, key=lambda l: l.epic_score, reverse=True)[:3]
    
    for i, legend in enumerate(top_3, 1):
        buffer.append(f"  {i}. {legend.title} ({legend.epic_score}/100)")
    
    return "\n".join(buffer)


async def cmd_mitos(ctx) -> str:
    """
    Mostra estatísticas globais do grimório.
    Uso: mitos
    """
    grimoire = ctx.world.grimoire
    
    if not grimoire.legends:
        return "O grimório está vazio. O mundo aguarda seus heróis."
    
    legends = list(grimoire.legends.values())
    
    # Estatísticas
    total_legends = len(legends)
    total_spread = sum(l.spread_count for l in legends)
    most_epic = max(legends, key=lambda l: l.epic_score)
    most_told = max(legends, key=lambda l: l.spread_count)
    
    # Protagonistas únicos
    protagonists = set(l.protagonist for l in legends)
    
    # Lenda mais antiga
    oldest = min(legends, key=lambda l: l.timestamp)
    
    import datetime
    age_days = (datetime.datetime.utcnow().timestamp() - oldest.timestamp) / 86400
    
    buffer = [
        "=== O GRIMÓRIO VIVO - ESTATÍSTICAS ===",
        "",
        f"Total de Lendas: {total_legends}",
        f"Heróis Únicos: {len(protagonists)}",
        f"Histórias Contadas: {total_spread}",
        f"Lenda Mais Antiga: {oldest.title} ({int(age_days)} dias atrás)",
        "",
        f"🏆 Lenda Mais Épica:",
        f"   '{most_epic.title}' ({most_epic.epic_score}/100)",
        "",
        f"📢 Lenda Mais Contada:",
        f"   '{most_told.title}' ({most_told.spread_count} vezes)",
        "",
        "Categorias:"
    ]
    
    categories = {}
    for legend in legends:
        categories[legend.category] = categories.get(legend.category, 0) + 1
    
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        buffer.append(f"  • {cat.capitalize()}: {count}")
    
    return "\n".join(buffer)


# ==============================================================================
# REGISTRO DOS COMANDOS
# ==============================================================================

def register_lore_commands(command_handler):
    """
    Adiciona os comandos de lore ao CommandHandler.
    Chame isso no __init__ do CommandHandler.
    """
    command_handler.register("lendas", cmd_lendas, ["legends", "histórias"])
    command_handler.register("ouvir", cmd_ouvir, ["listen", "escutar"])
    command_handler.register("reputacao", cmd_reputacao, ["rep", "reputation", "fama"])
    command_handler.register("mitos", cmd_mitos, ["myths", "grimorio"])