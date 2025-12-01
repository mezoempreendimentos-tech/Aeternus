import logging
import json
import random
import time
from typing import Dict, List, Tuple
from pathlib import Path

from backend.game.engines.magic.definitions import (
    Element, SpellFormula, SpellType, 
    MagicComponent, ResearchSession, ResearchState
)

logger = logging.getLogger(__name__)

class CatalystSystem:
    def __init__(self, magic_manager):
        self.magic_manager = magic_manager
        self.catalyst_templates: Dict[str, MagicComponent] = {}
        self.active_sessions: Dict[int, ResearchSession] = {} # PlayerID -> Session
        
        self.data_dir = Path("data")
        self.catalysts_path = self.data_dir / "catalysts.json"
        
        # Simulação de Inventário de Ingredientes (Mover para DB futuramente)
        self.player_catalysts: Dict[int, Dict[str, int]] = {} 

    def load_data(self):
        if not self.data_dir.exists(): self.data_dir.mkdir(parents=True)
        if not self.catalysts_path.exists():
            with open(self.catalysts_path, 'w') as f: json.dump({}, f)
        
        try:
            with open(self.catalysts_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for k, v in data.items():
                    self.catalyst_templates[k] = MagicComponent(vnum=k, **v)
        except Exception as e: logger.error(f"Erro Loading Catalysts: {e}")

    # --- GESTÃO DE SESSÃO (INTERATIVA) ---

    def start_research_session(self, player) -> str:
        """Inicia o transe de pesquisa."""
        room = self.magic_manager.world.get_room(player.location_vnum)
        
        # Validação: Só funciona em salas com flag LABORATORY
        if not room or "LABORATORY" not in room.flags:
            return "Este local não possui os aparatos arcanos necessários para pesquisa."
        
        if player.id in self.active_sessions:
            return "Você já está concentrado em um ritual! (Digite 'cancelar' para parar)"

        session = ResearchSession(player_id=player.id, state=ResearchState.WAITING_ELEMENTS)
        self.active_sessions[player.id] = session
        
        return (
            "🧪 **LABORATÓRIO ARCANO ATIVADO**\n"
            "Os queimadores acendem. O grimório em branco aguarda.\n\n"
            "PASSO 1: **Afinidade Elemental**\n"
            "Quais elementos você deseja fundir? (Digite separados por espaço, ex: 'fire air')"
        )

    def handle_input(self, player, text: str) -> str:
        """Processa a resposta do jogador durante a pesquisa."""
        session = self.active_sessions.get(player.id)
        if not session: return "Erro de sessão."
        
        text = text.lower().strip()
        if text == "cancelar":
            del self.active_sessions[player.id]
            return "🚫 Ritual abortado. Os reagentes foram guardados."

        if session.state == ResearchState.WAITING_ELEMENTS:
            return self._step_elements(session, text)
        elif session.state == ResearchState.WAITING_CATALYST:
            return self._step_catalyst(player, session, text)
        elif session.state == ResearchState.CONFIRMATION:
            return self._step_confirmation(player, session, text)
            
        return "Estado inválido."

    def _step_elements(self, session, text):
        elements = text.split()
        valid = []
        for e in elements:
            try: valid.append(Element(e).value)
            except ValueError: return f"Elemento '{e}' desconhecido. Tente: fire, water, air, earth, shadow..."
        
        if not valid: return "Especifique ao menos um elemento."
        session.selected_elements = valid
        session.state = ResearchState.WAITING_CATALYST
        return (
            f"✅ Base fixada: {', '.join(valid).upper()}.\n\n"
            "PASSO 2: **Catálise**\n"
            "Qual reagente você adicionará à mistura? (Digite o nome ou ID)"
        )

    def _step_catalyst(self, player, session, text):
        # Verifica posse (Simulado)
        found_id = None
        p_cats = self.player_catalysts.get(player.id, {})
        
        # Busca exata ou fuzzy
        if text in p_cats: found_id = text
        else:
            for pid in p_cats:
                tmpl = self.catalyst_templates.get(pid)
                if tmpl and text in tmpl.name.lower():
                    found_id = pid
                    break
        
        if not found_id: return f"Você não possui o ingrediente '{text}'."

        session.added_catalysts.append(found_id)
        session.state = ResearchState.CONFIRMATION
        return (
            f"⚗️ **{found_id}** dissolvido na mistura.\n"
            f"Total: {len(session.added_catalysts)} catalisadores.\n\n"
            "Opções:\n"
            "- Digite 'proximo' para adicionar mais reagentes.\n"
            "- Digite 'finalizar' para concluir o feitiço."
        )

    def _step_confirmation(self, player, session, text):
        if text in ["proximo", "próximo", "mais"]:
            session.state = ResearchState.WAITING_CATALYST
            return "O caldeirão borbulha. Aguardando próximo ingrediente..."
        if text == "finalizar":
            return self._finalize_research(player, session)
        return "Opção inválida. Digite 'proximo' ou 'finalizar'."

    def _finalize_research(self, player, session) -> str:
        del self.active_sessions[player.id]
        
        elements = session.selected_elements
        catalysts = session.added_catalysts
        
        # Consome Itens
        for cat in catalysts: 
            self.player_catalysts[player.id][cat] -= 1
            if self.player_catalysts[player.id][cat] <= 0: del self.player_catalysts[player.id][cat]

        # Lógica de Criação
        stability = self._calculate_stability(elements, catalysts)
        volatility = 1.0 - stability
        
        # Chance de Explosão
        if random.random() < (volatility * 0.4):
            return "💥 **FALHA CATASTRÓFICA!** A mistura instável detonou o laboratório. Reagentes perdidos."

        spell_type = self._determine_type(elements, catalysts)
        spell = self._generate_spell(player.name, elements, catalysts, spell_type, volatility)
        
        self.magic_manager.register_dynamic_spell(spell)
        
        stab_desc = "PERFEITA" if stability > 0.8 else "PERIGOSA"
        return (
            f"✨ **DESCOBERTA ARCANA!**\n"
            f"Nome: {spell.name}\n"
            f"Tipo: {spell_type.value.upper()}\n"
            f"Estabilidade: {int(stability*100)}% ({stab_desc})\n"
            f"Efeitos: {spell.description}\n\n"
            f"Use 'conjurar {spell.vnum}' para testar sua criação."
        )

    def _calculate_stability(self, elements, catalysts) -> float:
        score = 0.5
        if "fire" in elements and "water" in elements: score -= 0.3
        for cat_id in catalysts:
            cat = self.catalyst_templates.get(cat_id)
            if cat: score += cat.stability_bonus
        return max(0.1, min(1.0, score))

    def _determine_type(self, elements, catalysts) -> SpellType:
        # Lógica simples de peso
        is_summon = "life" in elements or any("core" in c for c in catalysts)
        is_enchant = "arcane" in elements or any("dust" in c for c in catalysts)
        
        if is_summon: return SpellType.SUMMONING
        if is_enchant: return SpellType.ENCHANTMENT
        return SpellType.OFFENSIVE

    def _generate_spell(self, creator, elements, catalysts, s_type, volatility):
        tier = len(elements)
        prim = Element(elements[0])
        vnum = int(time.time()) + random.randint(1, 1000)
        power = int(20 * tier * (1.0 + volatility))
        
        name = f"{creator}'s {prim.value.title()} {s_type.value.title()}"
        return SpellFormula(vnum=vnum, name=name, spell_type=s_type, tier=tier, 
                          primary_element=prim, mana_cost=10*tier, base_power=power,
                          volatility_score=volatility, created_by=creator,
                          description=f"Poder: {power}. Criada com {len(catalysts)} reagentes.")