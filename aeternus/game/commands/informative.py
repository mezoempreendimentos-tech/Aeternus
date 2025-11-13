from aeternus.game.world import world

async def do_who(connection, args):
    """Lista os jogadores conectados."""
    players = world.active_players
    count = len(players)
    
    header = f"\n\033[1;34m======== [ JOGADORES ONLINE: {count} ] ========\033[0m"
    await connection.send(header)
    
    for p in players:
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

async def do_score(connection, args):
    """Mostra a ficha completa do personagem."""
    p = connection.player
    
    # Tenta pegar o nome bonito da classe
    class_name = "Desconhecida"
    cls_obj = world.get_class(p.class_vnum)
    if cls_obj:
        class_name = cls_obj.name

    # Formatação da Ficha
    buffer = [
        f"\n\033[1;33m-----------------------------------------------------------------\033[0m",
        f" \033[1;37mNome:\033[0m {p.name} {p.title}",
        f" \033[1;37mClasse:\033[0m {class_name:<15} \033[1;37mNível:\033[0m {p.level}",
        f"\033[1;33m-----------------------------------------------------------------\033[0m",
        f" \033[1;36mHP:\033[0m {p.hp}/{p.max_hp}   \033[1;36mMana:\033[0m {p.mana}/{p.max_mana}   \033[1;36mStamina:\033[0m {p.stamina}/{p.max_stamina}",
        f"\033[1;33m--------------------------- ATRIBUTOS ---------------------------\033[0m",
        f" \033[1;32mForça:\033[0m        {p.strength:<2}    \033[1;32mInteligência:\033[0m {p.intelligence:<2}",
        f" \033[1;32mDestreza:\033[0m     {p.dexterity:<2}    \033[1;32mSabedoria:\033[0m    {p.wisdom:<2}",
        f" \033[1;32mConstituição:\033[0m {p.constitution:<2}    \033[1;32mCarisma:\033[0m      {p.charisma:<2}",
        f"\033[1;33m-----------------------------------------------------------------\033[0m\n"
    ]
    
    await connection.send("\n".join(buffer))