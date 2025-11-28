# backend/handlers/command_handler.py
import logging
import inspect
from typing import List, Dict, Callable, Optional
from backend.models.character import Character
from backend.game.world.world_manager import WorldManager
from backend.game.engines.combat.manager import CombatManager

logger = logging.getLogger(__name__)

class CommandContext:
    """O envelope de execução, contendo Mundo, Combate e Player."""
    def __init__(self, manager: WorldManager, combat: CombatManager, player: Character, args: List[str], raw: str):
        self.world = manager
        self.combat = combat
        self.player = player
        self.args = args
        self.raw_args = raw

class CommandHandler:
    def __init__(self, world_manager: WorldManager, combat_manager: CombatManager):
        self.world = world_manager
        self.combat = combat_manager
        self.commands: Dict[str, Callable] = {}
        self.aliases: Dict[str, str] = {}
        self._register_defaults()

    def register(self, keyword: str, func: Callable, aliases: List[str] = None):
        self.commands[keyword.lower()] = func
        if aliases:
            for alias in aliases:
                self.aliases[alias.lower()] = keyword.lower()

    def _register_defaults(self):
        # Importação tardia para evitar ciclo
        from backend.game.commands.core import (
            cmd_look, cmd_move, cmd_inventory, cmd_equipment, cmd_kill
        )
        from backend.game.commands.progression import cmd_remort  # <--- NOVO
        
        # --- COMANDOS BÁSICOS ---
        self.register("olhar", cmd_look, ["l", "look", "ver"])
        self.register("inventario", cmd_inventory, ["i", "inv", "mochila"])
        self.register("equipamento", cmd_equipment, ["eq", "equip"])
        
        # --- COMBATE ---
        self.register("matar", cmd_kill, ["k", "kill", "atacar"])

        # --- PROGRESSÃO (SAMSARA) ---
        self.register("renascer", cmd_remort, ["remort", "evoluir", "ascender"])

        # --- MOVIMENTAÇÃO (ROSA DOS VENTOS) ---
        self.register("norte", lambda ctx: cmd_move(ctx, "north"), ["n", "north"])
        self.register("sul", lambda ctx: cmd_move(ctx, "south"), ["s", "south"])
        self.register("leste", lambda ctx: cmd_move(ctx, "east"), ["e", "east", "l"])
        self.register("oeste", lambda ctx: cmd_move(ctx, "west"), ["w", "west", "o"])
        self.register("nordeste", lambda ctx: cmd_move(ctx, "northeast"), ["ne"])
        self.register("noroeste", lambda ctx: cmd_move(ctx, "northwest"), ["nw", "no"])
        self.register("sudeste", lambda ctx: cmd_move(ctx, "southeast"), ["se"])
        self.register("sudoeste", lambda ctx: cmd_move(ctx, "southwest"), ["sw", "so"])
        self.register("subir", lambda ctx: cmd_move(ctx, "up"), ["u", "up"])
        self.register("descer", lambda ctx: cmd_move(ctx, "down"), ["d", "down"])

    async def process(self, player_id: int, command_text: str) -> str:
        player = self.world.get_player(player_id)
        if not player: return "Erro: Player não encontrado."
        if not command_text.strip(): return ""

        parts = command_text.split()
        keyword = parts[0].lower()
        args = parts[1:]
        
        if keyword in self.aliases: keyword = self.aliases[keyword]
        func = self.commands.get(keyword)
        
        if not func: return "Comando desconhecido."

        try:
            ctx = CommandContext(self.world, self.combat, player, args, " ".join(args))
            
            if inspect.iscoroutinefunction(func):
                return await func(ctx)
            else:
                return func(ctx)
        except Exception as e:
            logger.error(f"Erro cmd '{command_text}': {e}", exc_info=True)
            return "Uma perturbação na trama mágica impediu sua ação."