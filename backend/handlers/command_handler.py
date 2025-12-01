# backend/handlers/command_handler.py
import logging
import inspect
from typing import List, Dict, Callable
from backend.models.character import Character
from backend.game.world.world_manager import WorldManager
from backend.game.engines.combat.manager import CombatManager
from backend.game.commands.core import cmd_look, cmd_move, cmd_inventory, cmd_equipment, cmd_kill

# --- IMPORTAÇÕES DE MÓDULOS OPCIONAIS ---
# Lore
try:
    from backend.game.commands.lore import (
        cmd_lendas, cmd_ouvir, cmd_reputacao, cmd_mitos
    )
except ImportError:
    cmd_lendas = cmd_ouvir = cmd_reputacao = cmd_mitos = None

# [NOVO] Ecologia
try:
    from backend.game.commands.ecology import (
        register_ecology_commands
    )
    ECOLOGY_AVAILABLE = True
except ImportError:
    ECOLOGY_AVAILABLE = False
# ----------------------------------------

logger = logging.getLogger(__name__)

class CommandContext:
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
        # Comandos Básicos
        self.register("olhar", cmd_look, ["l", "look", "ver"])
        self.register("inventario", cmd_inventory, ["i", "inv", "mochila"])
        self.register("equipamento", cmd_equipment, ["eq", "equip"])
        self.register("matar", cmd_kill, ["k", "kill", "atacar"])

        # Movimento
        dirs = {
            "norte": "north", "sul": "south", "leste": "east", "oeste": "west",
            "nordeste": "northeast", "noroeste": "northwest", "sudeste": "southeast", "sudoeste": "southwest",
            "subir": "up", "descer": "down"
        }
        for pt, en in dirs.items():
            self.register(pt, lambda ctx, d=en: cmd_move(ctx, d), [pt[0], en, en[0]])

        # --- LORE ---
        if cmd_lendas:
            self.register("lendas", cmd_lendas, ["legends", "histórias"])
            self.register("ouvir", cmd_ouvir, ["listen", "escutar"])
            self.register("reputacao", cmd_reputacao, ["rep", "fama"])
            self.register("mitos", cmd_mitos, ["myths", "grimorio"])

        # --- [NOVO] ECOLOGIA ---
        if ECOLOGY_AVAILABLE:
            register_ecology_commands(self)
            logger.info("🌿 Comandos Ecológicos: REGISTRADOS")
        else:
            logger.warning("⚠️ Módulo de Comandos Ecológicos não encontrado.")

    async def process(self, player_id: str, command_text: str) -> str:
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