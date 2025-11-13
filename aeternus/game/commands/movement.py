from aeternus.game.world import world

async def do_move(connection, direction):
    player = connection.player
    if not player: return

    current_room = player.room
    if not current_room:
        await connection.send("Estás perdido no vazio.")
        return

    exit_data = current_room.exits.get(direction)
    if not exit_data:
        await connection.send("Não podes ir por aí.")
        return

    target_vnum = exit_data.get('target_vnum')
    target_room = world.get_room(target_vnum)

    if not target_room:
        await connection.send(f"O caminho para {direction} leva ao abismo.")
        return

    # Movimento Físico
    if player in current_room.people:
        current_room.people.remove(player)
    
    player.room = target_room
    target_room.people.append(player)

    await connection.send("\n" + target_room.get_display())