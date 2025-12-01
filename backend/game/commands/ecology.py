# backend/game/commands/ecology.py
"""
Comandos de interação com o sistema ecológico.
"""

async def cmd_fauna(ctx) -> str:
    """
    Mostra a fauna local e condições.
    Uso: fauna [zona_id]
    """
    if not hasattr(ctx.world, 'ecology') or not ctx.world.ecology:
        return "A natureza está silenciosa (Sistema Offline)."
    
    zone_id = 1
    if ctx.world.rooms:
        current_room = ctx.world.get_room(ctx.player.location_vnum)
        if current_room:
            zone_id = current_room.zone_id

    # Se jogador especificou zona
    if ctx.args:
        try:
            zone_id = int(ctx.args[0])
        except ValueError:
            return "Use: fauna [numero_da_zona]"
    
    return ctx.world.ecology.get_zone_report(zone_id)

async def cmd_rastrear(ctx) -> str:
    """
    Tenta localizar um tipo de criatura.
    Uso: rastrear <nome>
    """
    if not hasattr(ctx.world, 'ecology') or not ctx.world.ecology:
        return "Seus instintos falham."
    
    if not ctx.args:
        return "Rastrear o quê? (Use: rastrear <nome_criatura>)"
    
    target = " ".join(ctx.args)
    # Teste de perícia poderia entrar aqui (Survival)
    return ctx.world.ecology.get_species_status(target)

async def cmd_clima(ctx) -> str:
    """
    Verifica o clima detalhado.
    """
    if not hasattr(ctx.world, 'ecology') or not ctx.world.ecology:
        return "Olhe para o céu... nada acontece."
    
    # Reutiliza o relatório da zona que já tem cabeçalho de clima
    # Futuramente pode ser separado
    return ctx.world.ecology.get_zone_report(1).split("-" * 40)[0] + "..."

def register_ecology_commands(command_handler):
    """Registro no handler principal."""
    command_handler.register("fauna", cmd_fauna, ["bio", "ecologia", "natureza"])
    command_handler.register("rastrear", cmd_rastrear, ["track", "buscar", "caçar"])
    command_handler.register("clima", cmd_clima, ["tempo", "weather"])