import sys
import yaml
import textwrap
import os
from pathlib import Path

# ==============================================================================
# SIMULAÇÃO DA ENGINE (Importando as classes que criamos)
# ==============================================================================
# Adiciona o diretório atual ao path para importar o 'aeternus'
sys.path.append(str(Path(".")))

try:
    from aeternus.game.objects.room import Room
except ImportError:
    # Fallback caso você ainda não tenha criado o __init__.py direito
    class Room:
        def __init__(self, vnum, name):
            self.vnum = vnum
            self.name = name
            self.description = ""
            self.exits = {}
        
        def add_exit(self, direction, target):
            self.exits[direction] = target

        def get_description_for(self, looker=None):
            # Simula a formatação do MUD
            desc = f"\033[1;36m{self.name}\033[0m \033[90m[VNUM: {self.vnum}]\033[0m\n"
            desc += "-" * 80 + "\n"
            desc += f"\033[37m{self.description}\033[0m\n"
            desc += "-" * 80 + "\n"
            
            if self.exits:
                exits_str = ", ".join([f"\033[1;33m{k}\033[0m" for k in self.exits.keys()])
                desc += f"\033[1;32m[Saídas: {exits_str}]\033[0m"
            else:
                desc += "\033[1;30m[Não há saídas visíveis]\033[0m"
            return desc

# ==============================================================================
# FERRAMENTAS DE BUSCA
# ==============================================================================
def encontrar_pasta_zona(zone_id_legacy):
    """Vasculha o atlas para achar onde a zona antiga foi parar."""
    raiz = Path("data/world/zones")
    
    # Maneira rápida: procurar no manifest.yaml
    for manifest in raiz.rglob("manifest.yaml"):
        try:
            with open(manifest, 'r', encoding='utf-8') as f:
                dados = yaml.safe_load(f)
                if str(dados.get('legacy_id')) == str(zone_id_legacy):
                    return manifest.parent
        except:
            continue
    return None

def carregar_sala(zone_id, room_vnum):
    pasta = encontrar_pasta_zona(zone_id)
    if not pasta:
        print(f"❌ Zona {zone_id} não encontrada no novo mundo.")
        return None

    arquivo_rooms = pasta / "rooms.yaml"
    if not arquivo_rooms.exists():
        print(f"❌ Arquivo rooms.yaml não encontrado em {pasta}.")
        return None

    with open(arquivo_rooms, 'r', encoding='utf-8') as f:
        salas = yaml.safe_load(f)
        
    # Procurar a sala específica
    dados_sala = next((r for r in salas if str(r['vnum']) == str(room_vnum)), None)
    
    if not dados_sala:
        print(f"❌ Sala {room_vnum} não encontrada dentro da Zona {zone_id}.")
        print(f"   (A zona tem {len(salas)} salas. Tente outro número).")
        return None

    # --- O MOMENTO DA CRIAÇÃO ---
    # Aqui transformamos dados mortos (dict) em objeto vivo (Class)
    sala_obj = Room(vnum=dados_sala['vnum'], name=dados_sala['name'])
    sala_obj.description = dados_sala['description']
    
    if 'exits' in dados_sala:
        for direcao, info in dados_sala['exits'].items():
            sala_obj.add_exit(direcao, info['target_vnum'])
            
    return sala_obj

# ==============================================================================
# MAIN
# ==============================================================================
if __name__ == "__main__":
    print("\n🔮 ORÁCULO DE VISÃO AETERNUS")
    print("Use para ver como uma sala ficou após a transmutação.\n")
    
    z_id = input("Digite o ID da Zona Antiga (ex: 10 para Midgaard): ").strip()
    r_id = input("Digite o VNUM da Sala (ex: 3001 para Praça): ").strip()
    
    print("\n" + "="*20 + " CARREGANDO REALIDADE " + "="*20 + "\n")
    
    sala = carregar_sala(z_id, r_id)
    
    if sala:
        print(sala.get_description_for(None))
        print("\n\n" + "="*60)