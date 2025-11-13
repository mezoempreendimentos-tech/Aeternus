import yaml
from pathlib import Path

def encontrar_a_praca():
    raiz = Path("data/world/zones")
    print(f"🔍 Varrendo o Multiverso em {raiz}...")
    
    target_local_id = "3001" # O ID antigo da praça
    
    for arquivo in raiz.rglob("rooms.yaml"):
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                salas = yaml.safe_load(f)
                if not salas: continue
                
                for sala in salas:
                    # Procura pelo ID local antigo (guardado no campo local_id)
                    # OU pelo nome da sala se o ID falhar
                    local_id = str(sala.get('local_id', ''))
                    vnum_global = sala.get('vnum')
                    nome = sala.get('name', '')
                    
                    # Critério 1: ID Local é 3001?
                    if local_id == target_local_id:
                        print(f"\n✅ ENCONTRADO POR ID!")
                        print(f"   Nome: {nome}")
                        print(f"   Arquivo: {arquivo}")
                        print(f"   VNUM GLOBAL (Copie isto): {vnum_global}")
                        print("-" * 40)
                        
                    # Critério 2: Nome contém 'Praça' ou 'Temple Square'?
                    elif "Temple Square" in nome or "Praça do Templo" in nome:
                        print(f"\n✅ ENCONTRADO POR NOME!")
                        print(f"   Nome: {nome}")
                        print(f"   VNUM GLOBAL: {vnum_global}")
                        print("-" * 40)

        except Exception as e:
            pass

if __name__ == "__main__":
    encontrar_a_praca()