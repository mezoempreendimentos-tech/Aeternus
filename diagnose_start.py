import sys
import os

# Adiciona o diretório atual ao path para imports funcionarem
sys.path.append(os.getcwd())

from aeternus.core.config import settings
from aeternus.game.world import world

def diagnostico():
    print("\n" + "="*60)
    print("🕵️  DIAGNÓSTICO DE COORDENADAS AETERNUS")
    print("="*60)
    
    # 1. Carregar o Mundo
    print(f"📂 Lendo dados de: {settings.ZONES_DIR}")
    world.load_assets()
    
    total_salas = len(world.room_blueprints)
    print(f"\n📊 Total de Salas Carregadas: {total_salas}")
    
    if total_salas == 0:
        print("💀 CRÍTICO: Nenhuma sala carregada. Verifique se rodou o transmuter_v7.py!")
        return

    # 2. Verificar o Alvo do .env
    alvo = str(settings.START_ROOM_VNUM)
    print(f"\n🎯 Alvo definido no .env: '{alvo}'")
    
    if alvo in world.room_blueprints:
        sala = world.room_blueprints[alvo]
        print(f"✅ SUCESSO! A sala existe.")
        print(f"   Nome: {sala.name}")
        print("   O problema pode estar no save do player antigo (tente criar um novo char).")
    else:
        print(f"❌ FALHA! A sala '{alvo}' NÃO existe na memória.")
        
        # 3. Buscar Candidatos (Sugestões)
        print("\n🔍 Procurando onde a Praça se escondeu...")
        candidatos = []
        
        for vnum, sala in world.room_blueprints.items():
            # Procura por ID local 3001 (fim da string)
            if vnum.endswith("3001"):
                candidatos.append((vnum, sala.name))
            # Ou procura por nome
            elif "Temple Square" in sala.name or "Praça" in sala.name:
                candidatos.append((vnum, sala.name))
        
        if candidatos:
            print(f"   Encontrei {len(candidatos)} possibilidades:")
            for vnum, nome in candidatos[:10]: # Mostra top 10
                print(f"   💡 ID REAL: {vnum}  | Nome: {nome}")
            
            print("\n👉 AÇÃO RECOMENDADA: Copie o ID REAL acima e coloque no seu .env")
        else:
            print("   ⚠️ Nenhuma sala parecida encontrada. O mundo foi gerado corretamente?")

if __name__ == "__main__":
    diagnostico()