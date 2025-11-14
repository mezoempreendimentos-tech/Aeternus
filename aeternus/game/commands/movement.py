from aeternus.game.world import world

async def do_move(connection, direction):
    player = connection.player
    if not player: return

    # 1. VERIFICAÇÃO DE COMBATE (NOVO)
    if player.fighting:
        await connection.send("\033[1;31mVOCÊ ESTÁ LUTANDO PELA SUA VIDA! Não pode simplesmente andar.\033[0m")
        await connection.send("Derrote seu inimigo ou use 'flee' para tentar fugir em pânico.")
        return

    # 2. Validações Normais
    current_room = player.room
    if not current_room:
        await connection.send("Estás perdido no vazio.")
        return

    exit_data = current_room.exits.get(direction)
    if not exit_data:
        await connection.send("Não podes ir por aí.")
        return

    target_vnum = exit_data.get('target_vnum')
    
    # Remove aspas extras se houver (Blindagem)
    if isinstance(target_vnum, str):
        target_vnum = target_vnum.strip("'")

    target_room = world.get_room(target_vnum)

    if not target_room:
        await connection.send(f"Caminho bloqueado (Sala {target_vnum} não encontrada).")
        return

    # 3. Movimento Físico
    if player in current_room.people:
        current_room.people.remove(player)
    
    player.room = target_room
    target_room.people.append(player)

    await connection.send("\n" + target_room.get_display())