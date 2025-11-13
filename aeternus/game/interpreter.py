from aeternus.game.commands.movement import do_move
from aeternus.game.commands.interaction import do_get, do_drop, do_inventory
from aeternus.game.commands.communication import (
    do_say, do_gossip, do_shout, do_tell, do_emote, do_broadcast, do_echo
)
from aeternus.game.commands.informative import do_who, do_look, do_score # <--- Import do_score

COMMANDS = {
    # Movimento
    'n': lambda c, a: do_move(c, 'north'),
    'north': lambda c, a: do_move(c, 'north'),
    's': lambda c, a: do_move(c, 'south'),
    'south': lambda c, a: do_move(c, 'south'),
    'e': lambda c, a: do_move(c, 'east'),
    'east': lambda c, a: do_move(c, 'east'),
    'w': lambda c, a: do_move(c, 'west'),
    'west': lambda c, a: do_move(c, 'west'),
    'u': lambda c, a: do_move(c, 'up'),
    'up': lambda c, a: do_move(c, 'up'),
    'd': lambda c, a: do_move(c, 'down'),
    'down': lambda c, a: do_move(c, 'down'),
    'ne': lambda c, a: do_move(c, 'northeast'),
    'nw': lambda c, a: do_move(c, 'northwest'),
    'se': lambda c, a: do_move(c, 'southeast'),
    'sw': lambda c, a: do_move(c, 'southwest'),

    # Interação
    'get': lambda c, a: do_get(c, a),
    'take': lambda c, a: do_get(c, a),
    'pegar': lambda c, a: do_get(c, a),
    'drop': lambda c, a: do_drop(c, a),
    'largar': lambda c, a: do_drop(c, a),
    'i': lambda c, a: do_inventory(c, a),
    'inv': lambda c, a: do_inventory(c, a),
    'inventory': lambda c, a: do_inventory(c, a),

    # Informação
    'who': lambda c, a: do_who(c, a),
    'quem': lambda c, a: do_who(c, a),
    'l': lambda c, a: do_look(c, a),
    'look': lambda c, a: do_look(c, a),
    'score': lambda c, a: do_score(c, a), # <--- Comando Score
    'f': lambda c, a: do_score(c, a),     # Atalho (Ficha)
    'ficha': lambda c, a: do_score(c, a),

    # Comunicação
    'say': lambda c, a: do_say(c, a),
    'gossip': lambda c, a: do_gossip(c, a),
    'chat': lambda c, a: do_gossip(c, a),
    'shout': lambda c, a: do_shout(c, a),
    'tell': lambda c, a: do_tell(c, a),
    'emote': lambda c, a: do_emote(c, a),
    'broadcast': lambda c, a: do_broadcast(c, a),
    'echo': lambda c, a: do_echo(c, a),
    
    'quit': None 
}

def find_command(user_input):
    if not user_input: return None, None
    if user_input in COMMANDS: return user_input, COMMANDS[user_input]
    matches = [k for k in COMMANDS.keys() if k.startswith(user_input)]
    if len(matches) == 1: return matches[0], COMMANDS[matches[0]]
    return None, None

async def handle_command(connection, line):
    if not line: return
    
    # Atalhos
    if line[0] == "'": line = "say " + line[1:]
    elif line[0] == ":": line = "emote " + line[1:]
    elif line[0] == ".": line = "gossip " + line[1:] 

    parts = line.split()
    raw_cmd = parts[0].lower()
    args = parts[1:]

    cmd_name, cmd_func = find_command(raw_cmd)

    if not cmd_name:
        await connection.send("Não entendo.")
        return

    if cmd_name == 'quit':
        await connection.send("Adeus.")
        connection.state = "DISCONNECT"
        return

    if cmd_func: await cmd_func(connection, args)