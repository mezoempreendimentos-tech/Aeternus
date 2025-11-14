from aeternus.game.world import world

async def do_goto(connection, args):
    """
    Teleporta o jogador para uma sala específica.
    Uso: goto <vnum>
    """
    if not args:
        await connection.send("Ir para onde? (Digite o VNUM da sala)")
        return

    target_vnum = args[0]
    player = connection.player
    
    # 1. Busca a sala no Atlas
    target_room = world.get_room(target_vnum)
    
    if not target_room:
        await connection.send(f"A sala '{target_vnum}' não existe na teia da realidade.")
        return

    # 2. Remove da sala atual
    if player.room and player in player.room.people:
        player.room.people.remove(player)

    # 3. Adiciona na sala nova
    player.room = target_room
    target_room.people.append(player)

    # 4. Feedback
    await connection.send(f"\033[1;35m*POOF* Você se materializa em: {target_room.name}\033[0m")
    await connection.send(target_room.get_display())