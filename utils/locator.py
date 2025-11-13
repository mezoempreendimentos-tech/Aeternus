import sys
import os
from pathlib import Path

# --- CORREÇÃO DE PATH ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.append(str(PROJECT_ROOT))
# ------------------------

from aeternus.core.config import settings
from aeternus.game.world import world

def diagnostico():
    print("\n" + "="*60)
    print("🕵️  [UTILS] DIAGNÓSTICO DE COORDENADAS AETERNUS")
    print("="*60)
    
    print(f"📂 Lendo dados de: {settings.ZONES_DIR}")
    world.load_assets()
    
    total_salas = len(world.room_blueprints)
    print(f"\n📊 Salas: {total_salas}")
    
    if total_salas == 0:
        print("💀 Nenhuma sala. Rode o utils/transmuter.py!")
        return

    alvo = str(settings.START_ROOM_VNUM)
    print(f"\n🎯 Alvo .env: '{alvo}'")
    
    if alvo in world.room_blueprints:
        print(f"✅ SUCESSO! Sala encontrada: {world.room_blueprints[alvo].name}")
    else:
        print(f"❌ FALHA! Sala não encontrada.")
        candidatos = []
        for vnum, sala in world.room_blueprints.items():
            if vnum.endswith("3001") or "Temple Square" in sala.name:
                candidatos.append((vnum, sala.name))
        
        if candidatos:
            print("💡 Sugestões:")
            for vnum, nome in candidatos[:5]:
                print(f"   ID: {vnum} | Nome: {nome}")

if __name__ == "__main__":
    diagnostico()