async def do_sleep(connection, args):
    player = connection.player
    if player.fighting:
        await connection.send("Dormir no meio da batalha? Loucura!")
        return
    
    if player.position == "sleeping":
        await connection.send("Você já está dormindo.")
        return
        
    player.position = "sleeping"
    await connection.send("Você se deita e fecha os olhos.")
    # Avisa a sala
    for p in player.room.people:
        if p != player and hasattr(p, 'connection') and p.connection:
            await p.connection.send(f"{player.name} se deita para dormir.")

async def do_rest(connection, args):
    player = connection.player
    if player.fighting:
        await connection.send("Termine a luta primeiro!")
        return
        
    if player.position == "resting":
        await connection.send("Você já está descansando.")
        return
        
    player.position = "resting"
    await connection.send("Você se senta para descansar os ossos.")
    for p in player.room.people:
        if p != player and hasattr(p, 'connection') and p.connection:
            await p.connection.send(f"{player.name} se senta e descansa.")

async def do_meditate(connection, args):
    player = connection.player
    if player.fighting:
        await connection.send("Impossível concentrar-se agora!")
        return
        
    if player.position == "meditating":
        await connection.send("Você já está em transe.")
        return
        
    player.position = "meditating"
    await connection.send("Você cruza as pernas e entra em meditação profunda.")
    for p in player.room.people:
        if p != player and hasattr(p, 'connection') and p.connection:
            await p.connection.send(f"{player.name} entra em transe meditativo.")

async def do_stand(connection, args):
    player = connection.player
    if player.position == "standing":
        await connection.send("Você já está de pé.")
        return
        
    if player.position == "sleeping":
        await connection.send("Você acorda e se levanta.")
    else:
        await connection.send("Você se levanta.")
        
    player.position = "standing"
    for p in player.room.people:
        if p != player and hasattr(p, 'connection') and p.connection:
            await p.connection.send(f"{player.name} se levanta.")

async def do_wake(connection, args):
    # Alias para stand se estiver dormindo
    await do_stand(connection, args)