import sys
import os
import yaml
from pathlib import Path

# Ajuste de Path para rodar da pasta utils ou raiz
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if "utils" not in str(Path(__file__).parent):
    PROJECT_ROOT = Path(__file__).parent

sys.path.append(str(PROJECT_ROOT))

from aeternus.core.config import settings

def carregar_yaml_simples(arquivo):
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except: return []

def diagnostico_resets():
    print("\n" + "="*60)
    print("🕵️  INVESTIGAÇÃO DE FALHAS DE REFERÊNCIA (RESETS)")
    print("="*60)

    # 1. Indexar o Mundo Existente
    print("📂 Indexando Blueprints (O que existe de verdade)...")
    
    db_rooms = set()
    db_mobs = set()
    db_items = set()

    # Varre Salas
    for f in settings.ZONES_DIR.rglob("rooms.yaml"):
        data = carregar_yaml_simples(f)
        if data:
            for entry in data: db_rooms.add(str(entry.get('vnum')))

    # Varre Mobs
    for f in settings.ZONES_DIR.rglob("mobs.yaml"):
        data = carregar_yaml_simples(f)
        if data:
            for entry in data: db_mobs.add(str(entry.get('vnum')))
            
    # Varre Itens
    for f in settings.ZONES_DIR.rglob("items.yaml"):
        data = carregar_yaml_simples(f)
        if data:
            for entry in data: db_items.add(str(entry.get('vnum')))

    print(f"   ✅ Salas Reais: {len(db_rooms)}")
    print(f"   ✅ Mobs Reais:  {len(db_mobs)}")
    print(f"   ✅ Itens Reais: {len(db_items)}")
    
    # Amostragem de IDs reais para comparação
    sample_room = list(db_rooms)[0] if db_rooms else "Nenhum"
    print(f"   📝 Exemplo de ID Real de Sala: '{sample_room}'")

    # 2. Analisar os Pedidos (Resets)
    print("\n📜 Analisando Pedidos de População (Resets)...")
    
    erros_mobs = 0
    erros_items = 0
    erros_salas = 0
    total_cmds = 0
    
    exemplos_erro = []

    for f in settings.ZONES_DIR.rglob("resets.yaml"):
        data = carregar_yaml_simples(f)
        if not data: continue
        
        for cmd in data:
            total_cmds += 1
            ctype = cmd.get('command')
            
            # Analisa comando 'M' (Carregar Mob em Sala)
            if ctype == 'M':
                mob_id = str(cmd.get('mob_vnum'))
                room_id = str(cmd.get('room_vnum'))
                
                mob_ok = mob_id in db_mobs
                room_ok = room_id in db_rooms
                
                if not mob_ok:
                    erros_mobs += 1
                    if len(exemplos_erro) < 5: exemplos_erro.append(f"Mob Missing: Pede '{mob_id}'")
                
                if not room_ok:
                    erros_salas += 1
                    if len(exemplos_erro) < 5: exemplos_erro.append(f"Room Missing: Pede '{room_id}'")

            # Analisa comando 'O' (Carregar Item em Sala)
            elif ctype == 'O':
                obj_id = str(cmd.get('obj_vnum'))
                room_id = str(cmd.get('room_vnum'))
                
                if obj_id not in db_items: erros_items += 1
                if room_id not in db_rooms: erros_salas += 1

    # 3. O Veredito
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE AUTOPSIA")
    print("="*60)
    print(f"Total de Comandos: {total_cmds}")
    print(f"💀 Mobs não encontrados:  {erros_mobs}")
    print(f"💀 Itens não encontrados: {erros_items}")
    print(f"💀 Salas não encontradas: {erros_salas}")
    print("-" * 60)
    
    if exemplos_erro:
        print("🔍 Amostra de Falhas (Compare com o ID Real lá em cima):")
        for erro in exemplos_erro:
            print(f"   ❌ {erro}")
            
    print("\n👉 DICA: Se o ID Real tem aspas e zeros (ex: '0101...') e o Pedido")
    print("   tem menos zeros ou é int, o erro está no Transmuter v10.")

if __name__ == "__main__":
    diagnostico_resets()