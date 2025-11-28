# simulate_battle.py
import asyncio
import logging
import json
import os
import shutil
from pathlib import Path

# Configura logger para imprimir no console
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("simulation")

# --- SETUP DE DADOS DE TESTE ---
DATA_DIR = Path("data")

# 1. CLASSE TUTORIAL (XP Boost)
TEST_CLASSES = {
    "novice": {
        "vnum": 1, "name": "Novato", "description": "Teste", "role": "tutorial",
        "base_hp": 100, "base_mana": 50, "base_sanity": 100, "xp_modifier": 1000.0,
        "attributes": {"strength": 15, "dexterity": 10, "constitution": 12, "intelligence": 10, "wisdom": 10, "charisma": 10, "luck": 10, "perception": 10, "willpower": 10},
        "starting_skills": [], "proficiencies": []
    }
}

# 2. NPC COM ATAQUES NATURAIS
TEST_NPCS = {
    "100001": {
        "vnum": 100001, 
        "name": "Rato Gigante de Teste", 
        "description": "Um rato sacrificial.",
        "level": 1, 
        "base_hp": 30, 
        "body_type": "rodent", 
        "sensory_visual": "Feio.",
        "flags": ["AGGRESSIVE"], 
        "loot_table": {},
        # AQUI: Definindo os verbos de ataque
        "natural_attacks": [
            {"name": "Dentes Afiados", "damage_type": "pierce", "verb": "morde", "damage_mult": 1.0},
            {"name": "Garras Sujas", "damage_type": "slash", "verb": "arranha", "damage_mult": 0.8}
        ]
    }
}

# 3. ITEM DE DEBUG
TEST_ITEMS = {
    "100001": {
        "vnum": 100001, "name": "Espada de Debug", "description": "Corta bugs.",
        "type": "weapon", "rarity": "common", "slot": "main_hand",
        "attack_verb": "fatia", # Verbo da arma
        "damage": {"min_dmg": 5, "max_dmg": 10, "damage_type": "slash"},
        "flags": ["SHARP"]
    }
}

# 4. ANATOMIA COM ARTIGOS
TEST_ANATOMY = {
    "rodent": {
        "description": "Rato",
        "parts": [
            {"id": "body", "name": "o Corpo", "hit_weight": 80, "hp_factor": 0.8, "flags": ["VITAL"]},
            {"id": "head", "name": "a Cabeça", "hit_weight": 20, "hp_factor": 0.2, "flags": ["VITAL"]}
        ]
    },
    "humanoid": {
        "description": "Humanoide Padrão",
        "parts": [
            {"id": "head", "name": "a Cabeça", "hit_weight": 5, "hp_factor": 0.15, "flags": ["VITAL"]},
            {"id": "torso", "name": "o Torso", "hit_weight": 45, "hp_factor": 1.0, "flags": ["VITAL"]},
            {"id": "right_arm", "name": "o Braço Direito", "hit_weight": 10, "hp_factor": 0.3, "flags": ["SEVERABLE"]},
            {"id": "left_arm", "name": "o Braço Esquerdo", "hit_weight": 10, "hp_factor": 0.3, "flags": ["SEVERABLE"]},
            {"id": "legs", "name": "as Pernas", "hit_weight": 30, "hp_factor": 0.4, "flags": ["MOVEMENT"]}
        ]
    }
}

TEST_ROOMS = {
    "100001": {
        "vnum": 100001, "zone_id": 1, "title": "Arena de Simulação",
        "description_day": "Lugar de testes.", "flags": ["INDOOR"], "exits": {}
    }
}

def setup_data():
    """Cria arquivos JSON vitais para o teste rodar."""
    if not DATA_DIR.exists():
        os.makedirs(DATA_DIR)
    
    # Salva arquivos
    with open(DATA_DIR / "classes.json", "w") as f: json.dump(TEST_CLASSES, f)
    with open(DATA_DIR / "npcs.json", "w") as f: json.dump(TEST_NPCS, f)
    with open(DATA_DIR / "items.json", "w") as f: json.dump(TEST_ITEMS, f)
    with open(DATA_DIR / "anatomy.json", "w") as f: json.dump(TEST_ANATOMY, f)
    with open(DATA_DIR / "rooms.json", "w") as f: json.dump(TEST_ROOMS, f)
    logger.info("📁 Dados de teste gerados em data/ (Com ataques naturais e anatomia corrigida)")

# --- A SIMULAÇÃO ---

async def run_simulation():
    # Imports tardios para garantir que os arquivos JSON já existam se a Factory carregar algo no import
    from backend.game.world.world_manager import WorldManager
    from backend.game.engines.combat.manager import CombatManager
    from backend.models.character import Character

    logger.info("\n🚀 INICIANDO SIMULAÇÃO DE COMBATE E LEVELING 🚀")
    logger.info("===============================================")

    # 1. Inicializa Mundo
    world = WorldManager()
    await world.start_up()
    
    combat = CombatManager(world)

    # 2. Cria Jogador
    hero = Character(
        id=999, player_id=999, name="Herói Tester",
        race_id="human", class_id="novice", location_vnum=100001
    )
    
    # Dá uma espada para ele
    sword = world.spawn_item(100001, 100001)
    if sword:
        hero.equipment["main_hand"] = sword.uid
        logger.info(f"⚔️ Jogador equipado com {sword.custom_name or 'Espada de Debug'}")

    world.add_player(hero)

    # 3. Spawna Monstro
    rat = world.spawn_npc(100001, 100001)
    if not rat:
        logger.error("Falha ao spawnar NPC!")
        return
    logger.info(f"🐀 Monstro Spawnado: {rat.name} (HP: {rat.current_hp})")

    # 4. Inicia Combate
    logger.info("\n🔔 --- INÍCIO DO COMBATE --- 🔔")
    await combat.start_combat(hero, rat)

    # 5. Loop de Batalha
    round_count = 1
    while rat.is_alive() and hero.hp.current > 0:
        logger.info(f"\n--- ROUND {round_count} ---")
        
        # Simula o tick de 2 segundos
        await combat.process_round()
        
        logger.info(f"Status: {hero.name} [HP:{hero.hp.current}] vs {rat.name} [HP:{rat.current_hp}]")
        round_count += 1
        
        # Pausa dramática pequena para ler o log
        await asyncio.sleep(0.5)

    # 6. Resultados
    logger.info("\n===============================================")
    if hero.hp.current > 0:
        logger.info("🏆 VITÓRIA DO JOGADOR!")
        logger.info(f"XP Final: {hero.experience}")
        logger.info(f"Nível Final: {hero.level}")
        
        if hero.level > 1:
            logger.info("✨ TESTE DE LEVEL UP: SUCESSO! ✨")
        else:
            logger.warning("⚠️ TESTE DE LEVEL UP: FALHOU (XP insuficiente?)")
    else:
        logger.info("💀 GAME OVER - O Rato venceu (Isso é constrangedor...)")

if __name__ == "__main__":
    setup_data()
    asyncio.run(run_simulation())