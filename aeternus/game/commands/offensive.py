from aeternus.game.commands.interaction import find_item_in_list

async def do_kill(connection, args):
    """Inicia combate com um alvo."""
    if not args:
        await connection.send("Matar quem?")
        return

    target_name = args[0]
    player = connection.player
    room = player.room

    # 1. Já está lutando?
    if player.fighting:
        await connection.send("Você já está ocupado lutando pela sua vida!")
        return

    # 2. Acha o alvo na sala (usamos a mesma função de busca de itens, adaptada)
    target = None
    
    # Procura Mobs/Players na sala
    for char in room.people:
        if char == player: continue
        # Verifica Keywords (se for mob) ou Nome (se for player)
        if hasattr(char, 'keywords'):
            if any(k.startswith(target_name.lower()) for k in char.keywords):
                target = char
                break
        elif target_name.lower() in char.name.lower():
            target = char
            break
            
    if not target:
        await connection.send("Não vejo ninguém com esse nome aqui.")
        return

    # 3. Inicia Combate
    await connection.send(f"\033[1;31mVocê grita e ataca {target.name}!\033[0m")
    
    if hasattr(target, 'connection') and target.connection:
        await target.connection.send(f"\033[1;31m{player.name} ATACA VOCÊ!\033[0m")

    # Linka os dois
    player.fighting = target
    target.fighting = player
    
    player.position = "fighting"
    target.position = "fighting"