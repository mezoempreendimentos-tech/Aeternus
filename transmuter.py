import os
import re
import yaml
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================
CAMINHO_LEGADO = Path("legacy_code/lib") 
ARQUIVO_ATLAS = Path("atlas_map.yaml")
CAMINHO_NOVO_MUNDO = Path("data/world/zones")

# ==============================================================================
# TRUQUE PARA FORÇAR ASPAS NO YAML
# ==============================================================================
class QuotedString(str):
    """Uma string que sempre será salva entre aspas simples no YAML."""
    pass

def quoted_string_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")

def multiline_presenter(dumper, data):
    if len(data.splitlines()) > 1:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

# Registra os apresentadores
yaml.add_representer(QuotedString, quoted_string_presenter)
yaml.add_representer(str, multiline_presenter)

# ==============================================================================
# FERRAMENTAS
# ==============================================================================
def limpar_texto(texto):
    if not texto: return ""
    try:
        texto = texto.encode('cp1252').decode('utf-8')
    except: pass
    return texto.strip().replace('\r', '')

def extrair_id_pasta(nome_pasta):
    match = re.match(r'^(\d+)_', nome_pasta)
    if match: return int(match.group(1))
    return 0

def gerar_vnum_universal(area, region, zone, local_id):
    """Retorna o ID de 11 Dígitos como QuotedString para forçar aspas."""
    try:
        local = int(local_id)
    except:
        local = 0 
    
    # Gera a string crua
    raw_vnum = f"{area:02d}{region:02d}{zone:03d}{local:04d}"
    # Retorna como objeto especial que o YAML vai aspar
    return QuotedString(raw_vnum)

# ==============================================================================
# PARSER
# ==============================================================================
class UniversalParser:
    def __init__(self):
        self.buffer = []
        self.idx = 0
        self.current_area = 0
        self.current_region = 0
        self.current_zone = 0

    def set_context(self, area, region, zone):
        self.current_area = area
        self.current_region = region
        self.current_zone = zone

    def to_global(self, local_vnum):
        return gerar_vnum_universal(self.current_area, self.current_region, self.current_zone, local_vnum)

    def load_file(self, filepath):
        if not filepath.exists(): return False
        try:
            with open(filepath, 'r', encoding='latin-1', errors='replace') as f:
                self.buffer = f.read().splitlines()
            self.idx = 0
            return True
        except: return False

    def get_next_line(self):
        while self.idx < len(self.buffer):
            line = self.buffer[self.idx].strip()
            self.idx += 1
            if not line or line.startswith('*'): continue
            return line
        return None

    def read_string(self, first_line=None):
        lines = []
        if first_line:
            clean = limpar_texto(first_line)
            if '~' in clean: return clean.split('~')[0].strip()
            lines.append(clean)
        while self.idx < len(self.buffer):
            line = self.buffer[self.idx]
            self.idx += 1
            if '~' in line:
                clean_part = limpar_texto(line.split('~')[0])
                lines.append(clean_part)
                return "\n".join(lines).strip()
            lines.append(limpar_texto(line))
        return ""

    def parse_rooms(self):
        rooms = []
        dir_map = {
            0:'north', 1:'east', 2:'south', 3:'west', 4:'up', 5:'down', 
            6:'northeast', 7:'northwest', 8:'southeast', 9:'southwest'
        }

        while True:
            line = self.get_next_line()
            if not line or line == '$': break
            
            if line.startswith('#'):
                local_vnum = line[1:]
                global_vnum = self.to_global(local_vnum)
                
                name = self.read_string(self.get_next_line())
                desc = self.read_string()
                self.get_next_line() 
                
                room = {
                    "vnum": global_vnum,
                    "local_id": local_vnum,
                    "name": name,
                    "description": desc,
                    "exits": {}
                }
                
                while True:
                    sub = self.get_next_line()
                    if not sub or sub == 'S': break
                    
                    if sub.startswith('D') and len(sub) > 1 and sub[1].isdigit():
                        dir_code = int(sub[1])
                        self.read_string()
                        self.get_next_line()
                        flags_line = self.get_next_line()
                        
                        if flags_line and dir_code in dir_map:
                            parts = flags_line.split()
                            if len(parts) >= 2:
                                target_local = parts[-1]
                                target_global = self.to_global(target_local)
                                
                                # Garante que o target também tenha aspas
                                room['exits'][dir_map[dir_code]] = {"target_vnum": target_global}
                    elif sub == 'E':
                        self.read_string(self.get_next_line())
                        self.read_string()
                rooms.append(room)
        return rooms

    def parse_mobs(self):
        mobs = []
        while True:
            line = self.get_next_line()
            if not line or line == '$': break
            if line.startswith('#'):
                local_vnum = line[1:]
                global_vnum = self.to_global(local_vnum)
                
                keys = self.read_string(self.get_next_line())
                short = self.read_string(self.get_next_line())
                long = self.read_string()
                look = self.read_string()
                while self.idx < len(self.buffer):
                    peek = self.buffer[self.idx].strip()
                    if peek.startswith('#') or peek == '$': break
                    self.idx += 1
                mobs.append({
                    "vnum": global_vnum, 
                    "name": short, 
                    "keywords": keys.split(), 
                    "description": look,
                    "long_desc": long
                })
        return mobs

    def parse_objs(self):
        objs = []
        while True:
            line = self.get_next_line()
            if not line or line == '$': break
            if line.startswith('#'):
                local_vnum = line[1:]
                global_vnum = self.to_global(local_vnum)
                
                keys = self.read_string(self.get_next_line())
                short = self.read_string(self.get_next_line())
                long = self.read_string()
                while self.idx < len(self.buffer):
                    peek = self.buffer[self.idx].strip()
                    if peek.startswith('#') or peek == '$': break
                    self.idx += 1
                objs.append({
                    "vnum": global_vnum,
                    "name": short, 
                    "keywords": keys.split(), 
                    "description": long
                })
        return objs

# ==============================================================================
# EXECUÇÃO
# ==============================================================================
def transmutar_mundo_v8():
    print("🛡️  INICIANDO TRANSMUTAÇÃO V8 (VNUMS BLINDADOS COM ASPAS)...")
    
    if not ARQUIVO_ATLAS.exists():
        print("❌ Atlas não encontrado.")
        return

    with open(ARQUIVO_ATLAS, 'r', encoding='utf-8') as f:
        atlas = yaml.safe_load(f)

    parser = UniversalParser()
    
    for area_key, regioes in atlas.items():
        if area_key == "99_nao_mapeado": continue
        
        area_id = extrair_id_pasta(area_key)

        for region_key, zonas in regioes.items():
            region_id = extrair_id_pasta(region_key)
            
            for zona_info in zonas:
                old_id = zona_info['old_id']
                folder_name = zona_info['new_folder_name']
                
                zone_prefix_match = re.match(r'^(\d+)_', folder_name)
                if zone_prefix_match:
                    zone_id = int(zone_prefix_match.group(1))
                else:
                    zone_id = old_id 

                parser.set_context(area_id, region_id, zone_id)
                
                path_zona = CAMINHO_NOVO_MUNDO / area_key / region_key / folder_name
                os.makedirs(path_zona, exist_ok=True)
                
                print(f"   Processando {folder_name}...", end="\r")

                # Salas
                wld_file = CAMINHO_LEGADO / "world/wld" / f"{old_id}.wld"
                if parser.load_file(wld_file):
                    with open(path_zona / "rooms.yaml", 'w', encoding='utf-8') as f:
                        yaml.dump(parser.parse_rooms(), f, default_flow_style=False, allow_unicode=True)
                
                # Mobs e Itens
                mob_file = CAMINHO_LEGADO / "world/mob" / f"{old_id}.mob"
                if parser.load_file(mob_file):
                    with open(path_zona / "mobs.yaml", 'w', encoding='utf-8') as f:
                        yaml.dump(parser.parse_mobs(), f, default_flow_style=False, allow_unicode=True)

                obj_file = CAMINHO_LEGADO / "world" / "obj" / f"{old_id}.obj"
                if parser.load_file(obj_file):
                    with open(path_zona / "items.yaml", 'w', encoding='utf-8') as f:
                        yaml.dump(parser.parse_objs(), f, default_flow_style=False, allow_unicode=True)

                # Manifest
                prefix = f"{area_id:02d}{region_id:02d}{zone_id:03d}"
                with open(path_zona / "manifest.yaml", 'w', encoding='utf-8') as f:
                    yaml.dump({
                        "zone_id": f"zone_{old_id}",
                        "vnum_prefix": QuotedString(prefix),
                        "vnum_range": QuotedString(f"{prefix}0000 - {prefix}9999")
                    }, f)

    print("\n✨ UNIVERSO REESCRITO. Todos os IDs estão protegidos por aspas.")

if __name__ == "__main__":
    transmutar_mundo_v8()