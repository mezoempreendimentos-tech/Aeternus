async def do_inventory(connection, args):
    """Mostra o que o jogador carrega."""
    player = connection.player
    if not player.inventory:
        await connection.send("Você não está carregando nada além do peso da sua consciência.")
        return

    buffer = ["\n\033[1;37mVocê está carregando:\033[0m"]
    for item in player.inventory:
        buffer.append(f"  {item.name}")
    
    await connection.send("\n".join(buffer) + "\n")

def find_item_in_list(target_name, item_list):
    target_name = target_name.lower()
    for item in item_list:
        if any(k.startswith(target_name) for k in item.keywords):
            return item
        if target_name in item.name.lower():
            return item
    return None

async def do_get(connection, args):
    if not args:
        await connection.send("Pegar o quê?")
        return

    player = connection.player
    target_name = args[0]
    room = player.room

    item = find_item_in_list(target_name, room.contents)
    
    if not item:
        await connection.send("Não vejo isso aqui.")
        return

    room.contents.remove(item)
    player.inventory.append(item)
    await connection.send(f"Você pega {item.name}.")

async def do_drop(connection, args):
    if not args:
        await connection.send("Largar o quê?")
        return

    player = connection.player
    target_name = args[0]
    
    item = find_item_in_list(target_name, player.inventory)
    
    if not item:
        await connection.send("Você não tem isso.")
        return

    player.inventory.remove(item)
    player.room.contents.append(item)
    await connection.send(f"Você larga {item.name}.")