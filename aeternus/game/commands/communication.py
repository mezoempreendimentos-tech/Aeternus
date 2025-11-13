from aeternus.game.world import world

# ==============================================================================
# UTILITÁRIOS DE ALCANCE
# ==============================================================================
def get_zone_prefix(room):
    """
    Retorna a 'Assinatura da Zona' (AA RR ZZZ).
    VNUM Formato: AARRZZZRRRR (11 digitos).
    Pegamos os primeiros 7 caracteres.
    """
    if not room or not room.vnum:
        return "0000000"
    # Retorna os primeiros 7 digitos (Area + Region + Zone)
    return str(room.vnum)[:7]

async def send_to_char(target, message):
    """Entrega a mensagem se o alvo tiver conexão ativa."""
    if hasattr(target, 'connection') and target.connection:
        await target.connection.send(message)

def find_player_online(name):
    """Busca um jogador na lista de ativos (busca parcial)."""
    name = name.lower()
    for player in world.active_players:
        if player.name.lower().startswith(name):
            return player
    return None

# ==============================================================================
# CANAIS DE JOGADOR
# ==============================================================================

async def do_say(connection, args):
    """Fala para a sala (Local)."""
    if not args:
        await connection.send("Dizer o quê?")
        return

    message = " ".join(args)
    player = connection.player
    
    # Feedback para quem fala
    await connection.send(f"\033[1;36mVocê diz: '{message}'\033[0m")

    # Envia para outros na sala
    text_others = f"\033[1;36m{player.name} diz: '{message}'\033[0m"
    for target in player.room.people:
        if target != player:
            await send_to_char(target, text_others)

async def do_gossip(connection, args):
    """Chat Global (Ondas de Rádio para todos)."""
    if not args:
        await connection.send("Gossip o quê?")
        return

    message = " ".join(args)
    player = connection.player
    
    # Formatação Magenta (Padrão MUD)
    text_global = f"\033[1;35m[GOSSIP] {player.name}: {message}\033[0m"

    # Simples e Direto: Manda para todo mundo na lista
    for target in world.active_players:
        await send_to_char(target, text_global)

async def do_shout(connection, args):
    """Grita para a Zona inteira (Area + Region + Zone)."""
    if not args:
        await connection.send("Gritar o quê?")
        return

    message = " ".join(args).upper() # Gritos são em maiúsculas!
    player = connection.player
    
    if not player.room: return

    my_zone = get_zone_prefix(player.room)
    
    text_shout = f"\033[1;31m{player.name} GRITA: '{message}'\033[0m"
    await connection.send(f"\033[1;31mVocê GRITA: '{message}'\033[0m")

    for target in world.active_players:
        if target != player and target.room:
            # Se o alvo estiver na mesma zona (mesmo prefixo de 7 digitos)
            if get_zone_prefix(target.room) == my_zone:
                await send_to_char(target, text_shout)

async def do_tell(connection, args):
    """Conversa telepática privada."""
    if len(args) < 2:
        await connection.send("Tell quem o quê? (Ex: tell conan oi)")
        return

    target_name = args[0]
    message = " ".join(args[1:])
    player = connection.player

    target = find_player_online(target_name)
    
    if not target:
        await connection.send(f"Não sinto a mente de '{target_name}' neste plano.")
        return

    # Formatação Vermelha/Rosa
    text_to_target = f"\033[1;31m*{player.name}* diz-lhe: {message}\033[0m"
    text_to_self = f"\033[1;31mVocê diz para *{target.name}*: {message}\033[0m"

    await send_to_char(target, text_to_target)
    await connection.send(text_to_self)

async def do_emote(connection, args):
    """Ação narrativa."""
    if not args: return
    action = " ".join(args)
    
    # Formatação Amarela
    text = f"\033[1;33m{connection.player.name} {action}\033[0m"
    
    for target in connection.player.room.people:
        await send_to_char(target, text)

# ==============================================================================
# CANAIS DE SISTEMA (ECHO / BROADCAST)
# ==============================================================================

async def do_broadcast(connection, args):
    """Mensagem Oficial do Servidor para TODOS."""
    if not args:
        await connection.send("Broadcast o quê?")
        return
    
    message = " ".join(args)
    # Fundo Azul, Letra Branca (Destaque Absoluto)
    text = f"\n\033[44;1;37m[SISTEMA]: {message}\033[0m\n"
    
    for target in world.active_players:
        await send_to_char(target, text)

async def do_echo(connection, args):
    """
    Eco flexível para eventos.
    Uso: echo <room|zone|global> <mensagem>
    """
    if len(args) < 2:
        await connection.send("Uso: echo <room|zone|global> <mensagem>")
        return

    scope = args[0].lower()
    message = " ".join(args[1:])
    player = connection.player
    
    # Amarelo Brilhante
    text = f"\033[1;33m[EVENTO]: {message}\033[0m"

    # 1. Apenas na Sala
    if scope in ['room', 'sala']:
        for target in player.room.people:
            await send_to_char(target, text)
        await connection.send("--> Echo Room enviado.")

    # 2. Na Zona Inteira
    elif scope in ['zone', 'zona']:
        if not player.room: return
        my_zone = get_zone_prefix(player.room)
        count = 0
        for target in world.active_players:
            if target.room and get_zone_prefix(target.room) == my_zone:
                await send_to_char(target, text)
                count += 1
        await connection.send(f"--> Echo enviado para a zona (Ouvintes: {count}).")

    # 3. Global (Mundo todo)
    elif scope in ['global', 'all', 'mundo', 'area', 'region']:
        for target in world.active_players:
            await send_to_char(target, text)
        await connection.send("--> Echo enviado para o mundo inteiro.")
    
    else:
        await connection.send("Escopo inválido. Use: room, zone, global.")