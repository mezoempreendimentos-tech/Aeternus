import yaml
import math
import sys
import os
import re
from pathlib import Path
from collections import deque

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CAMINHO_ZONAS = PROJECT_ROOT / "data" / "world" / "zones"

ARQUIVO_DESCR = SCRIPT_DIR / "areas_descr" 
ARQUIVO_SAIDA = SCRIPT_DIR / "atlas_map.yaml"

# Ponto de Partida: A Praça de Midgaard
START_VNUM_HINT = "010103003001" 

# ==============================================================================
# CONFIGURAÇÃO YAML
# ==============================================================================
class QuotedString(str): pass
def quoted_string_presenter(dumper, data): return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")
def multiline_presenter(dumper, data):
    if len(data.splitlines()) > 1: return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)
yaml.add_representer(QuotedString, quoted_string_presenter)
yaml.add_representer(str, multiline_presenter)

# ==============================================================================
# INTELIGÊNCIA DE LORE (CLASSIFICAÇÃO)
# ==============================================================================
def classificar_zona(zid, nome_raw, avg_x, avg_y, avg_z):
    """
    Define a Região dentro de Vitalia baseada em Nome, ID e Posição.
    """
    nome = nome_raw.lower()
    distancia_centro = math.sqrt(avg_x**2 + avg_y**2)
    
    # --- GRANDE ÁREA: MUNDO VITALIA (Padrão) ---
    AREA_DEFAULT = "01_mundo_vitalia"

    # 1. SISTEMA & LIMBO (IDs muito baixos)
    if zid < 3:
        return AREA_DEFAULT, "00_sistema_limbo"

    # 2. PANTEÃO DIVINO (Palavras-chave sagradas)
    palavras_divinas = ["god", "deus", "olympus", "olimpo", "asgard", "heaven", "divin", "zodiac"]
    if any(p in nome for p in palavras_divinas):
        return AREA_DEFAULT, "04_panteao_divino"

    # 3. IMPÉRIO DE THALOS (Leste / Deserto)
    # IDs 50-59 são tradicionalmente Thalos. Ou se tiver nome, ou se estiver muito a Leste.
    if (50 <= zid <= 59) or "thalos" in nome or "pirâmide" in nome or "pyramid" in nome or "desert" in nome:
        return AREA_DEFAULT, "02_imperio_thalos"
    
    if avg_x > 150: # Muito a leste, assume influência de Thalos
        return AREA_DEFAULT, "02_imperio_thalos"

    # 4. NATUREZA & SUBMUNDO (Florestas, Minas, Esgotos)
    if "sewer" in nome or "esgoto" in nome or "under" in nome or avg_z < -2:
        return AREA_DEFAULT, "05_submundo_sombrio"
        
    if (60 <= zid <= 79) or "forest" in nome or "floresta" in nome or "haon" in nome or "elf" in nome:
        return AREA_DEFAULT, "03_grande_natureza"
        
    if (40 <= zid <= 49) or "moria" in nome or "dwar" in nome or "anão" in nome or "mine" in nome or "mountain" in nome:
        return AREA_DEFAULT, "03_grande_natureza"

    # 5. REINO DE MIDGAARD (Centro)
    # Se for Zona 10-39, ou tiver Midgaard no nome, ou estiver perto do (0,0)
    if (3 <= zid <= 39) or "midgaard" in nome or "chess" in nome:
        return AREA_DEFAULT, "01_reino_midgaard"
    
    if distancia_centro < 80: # Proximidade geográfica
        return AREA_DEFAULT, "01_reino_midgaard"

    # 6. O RESTO (Terras Distantes)
    return AREA_DEFAULT, "06_terras_fronteiricas"

# ==============================================================================
# FERRAMENTAS TÉCNICAS
# ==============================================================================
def carregar_nomes_originais():
    nomes = {}
    if not ARQUIVO_DESCR.exists(): return nomes
    with open(ARQUIVO_DESCR, 'r', encoding='latin-1', errors='ignore') as f:
        buffer = f.read()
        matches = re.findall(r"==> (\d+)\.zon <==\s*#\d+\s*([^~]+)~", buffer)
        for mid, mname in matches:
            nomes[int(mid)] = mname.strip().replace('\n', ' ')
    return nomes

def carregar_mundo_inteiro():
    print("🌍 Carregando dados para análise geopolítica...")
    world_map = {} 
    arquivos = list(CAMINHO_ZONAS.rglob("rooms.yaml"))
    for arq in arquivos:
        try:
            with open(arq, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if not data: continue
                for room in data:
                    vnum = str(room.get('vnum'))
                    try:
                        if len(vnum) >= 7: zone_id = int(vnum[4:7])
                        else: zone_id = 0
                    except: zone_id = 0
                    room['zone_id'] = zone_id
                    world_map[vnum] = room
        except: pass
    print(f"✅ {len(world_map)} locais analisados.")
    return world_map

def encontrar_inicio(world_map):
    if START_VNUM_HINT in world_map: return START_VNUM_HINT
    for vnum, room in world_map.items():
        if "Temple Square" in room.get('name', '') or "Praça" in room.get('name', ''):
            return vnum
    if world_map: return list(world_map.keys())[0]
    return None

# ==============================================================================
# EXPLORADOR
# ==============================================================================
def explorar_mundo():
    world_map = carregar_mundo_inteiro()
    if not world_map:
        print("❌ Erro: Mundo vazio. Rode o transmuter antes.")
        return

    start_vnum = encontrar_inicio(world_map)
    print(f"🏃 Expedição partindo de: {start_vnum}")
    
    queue = deque([(start_vnum, 0, 0, 0)]) # VNUM, X, Y, Z
    visited = {start_vnum}
    zone_stats = {} # {zid: {x, y, z, n}}
    
    vectors = {
        'north': (0, 1, 0), 'south': (0, -1, 0),
        'east': (1, 0, 0), 'west': (-1, 0, 0),
        'up': (0, 0, 1), 'down': (0, 0, -1),
        'northeast': (1, 1, 0), 'northwest': (-1, 1, 0),
        'southeast': (1, -1, 0), 'southwest': (-1, -1, 0)
    }

    # 1. Caminhada (BFS)
    while queue:
        curr_vnum, x, y, z = queue.popleft()
        room = world_map.get(curr_vnum)
        if not room: continue
        
        zid = room['zone_id']
        if zid not in zone_stats: zone_stats[zid] = {'x':0, 'y':0, 'z':0, 'n':0}
        
        zone_stats[zid]['x'] += x
        zone_stats[zid]['y'] += y
        zone_stats[zid]['z'] += z
        zone_stats[zid]['n'] += 1
        
        if 'exits' in room:
            for direction, info in room['exits'].items():
                target = str(info.get('target_vnum')).strip("'")
                if target not in visited and target in world_map:
                    visited.add(target)
                    dx, dy, dz = vectors.get(direction, (0,0,0))
                    queue.append((target, x+dx, y+dy, z+dz))

    # 2. Desenho do Mapa
    print("🗺️  Desenhando fronteiras...")
    nomes_originais = carregar_nomes_originais()
    novo_atlas = {}
    zonas_conectadas = set()

    # Processa zonas conectadas
    for zid, stats in zone_stats.items():
        zonas_conectadas.add(zid)
        avg_x = int(stats['x'] / stats['n'])
        avg_y = int(stats['y'] / stats['n'])
        avg_z = int(stats['z'] / stats['n'])
        
        nome_real = nomes_originais.get(zid, f"Zona {zid}")
        area, regiao = classificar_zona(zid, nome_real, avg_x, avg_y, avg_z)
        
        nome_pasta = re.sub(r'[^a-z0-9]', '', nome_real.lower().replace(' ', '_'))
        
        entry = {
            "old_id": zid,
            "original_name": nome_real,
            "new_folder_name": f"{zid:03d}_{nome_pasta}",
            "pos": f"{avg_x},{avg_y}"
        }
        
        if area not in novo_atlas: novo_atlas[area] = {}
        if regiao not in novo_atlas[area]: novo_atlas[area][regiao] = []
        novo_atlas[area][regiao].append(entry)

    # Processa zonas isoladas
    all_zones = set(r['zone_id'] for r in world_map.values())
    missing = all_zones - zonas_conectadas
    
    if missing:
        area_miss = "99_terras_perdidas" # Area separada
        reg_miss = "00_desconhecido"
        if area_miss not in novo_atlas: novo_atlas[area_miss] = {}
        if reg_miss not in novo_atlas[area_miss]: novo_atlas[area_miss][reg_miss] = []
        
        for zid in missing:
            nome_real = nomes_originais.get(zid, f"Zona {zid}")
            nome_pasta = re.sub(r'[^a-z0-9]', '', nome_real.lower().replace(' ', '_'))
            entry = {
                "old_id": zid,
                "original_name": nome_real,
                "new_folder_name": f"{zid:03d}_{nome_pasta}",
                "pos": "ISOLADA"
            }
            novo_atlas[area_miss][reg_miss].append(entry)

    # Ordenação
    for area in novo_atlas:
        for reg in novo_atlas[area]:
            novo_atlas[area][reg].sort(key=lambda x: x['old_id'])

    # Salvar
    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
        yaml.dump(novo_atlas, f, sort_keys=True, allow_unicode=True, default_flow_style=False)

    print(f"✨ MAPA GEOPOLÍTICO CONCLUÍDO.")
    print(f"   Zonas Integradas: {len(zonas_conectadas)}")
    print(f"   Zonas Isoladas:   {len(missing)}")
    print(f"📄 Verifique: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    explorar_mundo()