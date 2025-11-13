from aeternus.game.world import world

async def do_who(connection, args):
    """Lista os jogadores conectados."""
    players = world.active_players
    count = len(players)
    
    header = f"\n\033[1;34m======== [ JOGADORES ONLINE: {count} ] ========\033[0m"
    await connection.send(header)
    
    for p in players:
        # Formato: [Novato] Conan o Bárbaro
        title = getattr(p, 'title', 'o Viajante')
        line = f"[{title}] {p.name}"
        await connection.send(line)
        
    await connection.send("\033[1;34m========================================\033[0m\n")

async def do_look(connection, args):
    """Olha para a sala."""
    if connection.player and connection.player.room:
        await connection.send(connection.player.room.get_display())
    else:
        await connection.send("Você flutua no vazio.")