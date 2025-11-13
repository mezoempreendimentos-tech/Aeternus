import os
import re
import yaml
import sys
import logging
from pathlib import Path

# CONFIGURAÇÃO
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CAMINHO_LEGADO = PROJECT_ROOT / "legacy_code" / "lib"
ARQUIVO_ATLAS = SCRIPT_DIR / "atlas_map.yaml"
CAMINHO_NOVO_MUNDO = PROJECT_ROOT / "data" / "world" / "zones"
LOG_FILE = SCRIPT_DIR / "transmuter_debug.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', filemode='w', encoding='utf-8')
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
logging.getLogger('').addHandler(console)

def log(msg): logging.info(msg)
def warn(msg): logging.warning(msg); print(f"⚠️  {msg}")
def error(msg): logging.error(msg); print(f"❌ {msg}")

# YAML CONFIG
class QuotedString(str): pass
def quoted_string_presenter(dumper, data): return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")
def multiline_presenter(dumper, data):
    if len(data.splitlines()) > 1: return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)
yaml.add_representer(QuotedString, quoted_string_presenter)
yaml.add_representer(str, multiline_presenter)

# FERRAMENTAS
def limpar_texto(texto):
    if not texto: return ""
    try: texto = texto.encode('cp1252').decode('utf-8')
    except: pass
    return texto.strip().replace('\r', '')

def limpar_keywords(raw_string):
    stop_words = {"o", "a", "um", "uma", "de", "da", "do"}
    raw_list = raw_string.split()
    clean_list = [k for k in raw_list if k.lower() not in stop_words and len(k) > 1]
    return clean_list if clean_list else raw_list

def extrair_id_pasta(nome_pasta):
    match = re.match(r'^(\d+)_', nome_pasta)
    if match: return int(match.group(1))
    return 0

def gerar_vnum_universal(area, region, zone, local_id):
    try: local = int(local_id)
    except: local = 0 
    # ATUALIZAÇÃO: 5 DÍGITOS PARA ID LOCAL
    raw_vnum = f"{area:02d}{region:02d}{zone:03d}{local:05d}"
    return QuotedString(raw_vnum)

def indexar_arquivos_legado():
    index = {'wld': {}, 'mob': {}, 'obj': {}, 'zon': {}}
    pastas = {'wld': CAMINHO_LEGADO/"world/wld", 'mob': CAMINHO_LEGADO/"world/mob", 'obj': CAMINHO_LEGADO/"world/obj", 'zon': CAMINHO_LEGADO/"world/zon"}
    log("📂 Indexando arquivos legado...")
    for tipo, path in pastas.items():
        if not path.exists():
            warn(f"Pasta não encontrada: {path}")
            continue
        for arquivo in path.glob(f"*.{tipo}"):
            try:
                stem = arquivo.stem
                if stem.isdigit(): index[tipo][int(stem)] = arquivo
            except: pass
    return index

# PARSER
class UniversalParser:
    def __init__(self):
        self.buffer = []
        self.idx = 0
        self.filename = ""
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
        if not filepath: return False
        self.filename = filepath.name
        try:
            with open(filepath, 'rb') as f: raw = f.read()
            try: content = raw.decode('cp1252')
            except: content = raw.decode('latin-1', errors='replace')
            self.buffer = content.splitlines()
            self.idx = 0
            log(f"   [LOAD] Carregado {filepath.name}")
            return True
        except Exception as e:
            error(f"Falha ao ler {filepath}: {e}")
            return False

    def get_next_line(self):
        while self.idx < len(self.buffer):
            line = self.buffer[self.idx].strip()
            self.idx += 1
            if not line or line.startswith('*'): continue
            return line
        return None

    def peek_next_line(self):
        temp_idx = self.idx
        while temp_idx < len(self.buffer):
            line = self.buffer[temp_idx].strip()
            if not line or line.startswith('*'):
                temp_idx += 1
                continue
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
        dir_map = {0:'north', 1:'east', 2:'south', 3:'west', 4:'up', 5:'down', 6:'northeast', 7:'northwest', 8:'southeast', 9:'southwest'}
        line = self.get_next_line()
        while line:
            if line == '$': break
            if line.startswith('#'):
                local = line[1:]
                try:
                    name = self.read_string(self.get_next_line())
                    desc = self.read_string()
                    self.get_next_line() 
                    room = {"vnum": self.to_global(local), "name": name, "description": desc, "exits": {}}
                    while True:
                        prox = self.peek_next_line()
                        if not prox or prox == '$' or prox.startswith('#'): break
                        sub = self.get_next_line()
                        if sub.startswith('D') and len(sub) > 1 and sub[1].isdigit():
                            dcode = int(sub[1])
                            self.read_string(); self.get_next_line(); flags = self.get_next_line()
                            if flags and dcode in dir_map:
                                parts = flags.split()
                                if len(parts) >= 2:
                                    room['exits'][dir_map[dcode]] = {"target_vnum": self.to_global(parts[-1])}
                        elif sub == 'S': break
                        elif sub == 'E': self.read_string(self.get_next_line()); self.read_string()
                    rooms.append(room)
                except Exception as e: error(f"Erro sala #{local}: {e}")
            line = self.get_next_line()
        return rooms

    def parse_mobs(self):
        mobs = []
        line = self.get_next_line()
        while line:
            if line == '$': break
            if line.startswith('#'):
                local = line[1:]
                try:
                    keys = self.read_string(self.get_next_line())
                    short = self.read_string(self.get_next_line())
                    room_msg = self.read_string()
                    look_desc = self.read_string()
                    mobs.append({
                        "vnum": self.to_global(local),
                        "name": short, 
                        "keywords": limpar_keywords(keys),
                        "description": room_msg,
                        "long_desc": look_desc
                    })
                    while True:
                        prox = self.peek_next_line()
                        if not prox or prox == '$' or prox.startswith('#'): break
                        self.get_next_line()
                except: pass
            line = self.get_next_line()
        return mobs

    def parse_objs(self):
        objs = []
        line = self.get_next_line()
        while line:
            if line == '$': break
            if line.startswith('#'):
                local = line[1:]
                try:
                    keys = self.read_string(self.get_next_line())
                    short = self.read_string(self.get_next_line())
                    room_msg = self.read_string()
                    action_desc = self.read_string()
                    objs.append({
                        "vnum": self.to_global(local),
                        "name": short, 
                        "keywords": limpar_keywords(keys),
                        "description": room_msg,
                        "action_desc": action_desc
                    })
                    while True:
                        prox = self.peek_next_line()
                        if not prox or prox == '$' or prox.startswith('#'): break
                        self.get_next_line()
                except: pass
            line = self.get_next_line()
        return objs

    def parse_zone_resets(self):
        resets = []
        line = self.get_next_line()
        if line and line.startswith('#'):
            attempts = 0
            while attempts < 5:
                peek = self.buffer[self.idx].strip()
                if not peek: self.idx += 1; continue
                if '~' in peek: self.read_string(); break
                if peek[0].isdigit() and len(peek.split()) >= 3: self.get_next_line(); break
                self.idx += 1
                attempts += 1

        while True:
            line = self.get_next_line()
            if not line or line == '$': break
            parts = line.split()
            if not parts: continue
            cmd = parts[0]
            if cmd not in ['M', 'O', 'G', 'E', 'D', 'R', 'P', 'T']: continue
            entry = {"command": cmd}
            try:
                if cmd == 'M' and len(parts) >= 5: 
                    entry.update({"mob_vnum": self.to_global(parts[2]), "limit": int(parts[3]), "room_vnum": self.to_global(parts[4])})
                elif cmd == 'O' and len(parts) >= 5:
                    entry.update({"obj_vnum": self.to_global(parts[2]), "limit": int(parts[3]), "room_vnum": self.to_global(parts[4])})
                elif cmd == 'G' and len(parts) >= 4:
                    entry.update({"obj_vnum": self.to_global(parts[2]), "limit": int(parts[3])})
                elif cmd == 'E' and len(parts) >= 5:
                    entry.update({"obj_vnum": self.to_global(parts[2]), "limit": int(parts[3]), "slot": int(parts[4])})
                elif cmd == 'D' and len(parts) >= 5:
                    entry.update({"room_vnum": self.to_global(parts[2]), "door": int(parts[3]), "state": int(parts[4])})
                if len(entry) > 1: resets.append(entry)
            except: continue
        return resets

def transmutar_mundo_v16():
    print("🛡️  [UTILS] TRANSMUTER V16 (12-DIGIT SUPPORT) RODANDO...")
    
    if not ARQUIVO_ATLAS.exists(): return
    file_index = indexar_arquivos_legado()
    with open(ARQUIVO_ATLAS, 'r', encoding='utf-8') as f: atlas = yaml.safe_load(f)
    parser = UniversalParser()
    
    for area_key, regioes in atlas.items():
        if area_key == "99_nao_mapeado": continue
        area_id = extrair_id_pasta(area_key)
        for region_key, zonas in regioes.items():
            region_id = extrair_id_pasta(region_key)
            for zona_info in zonas:
                old_id = zona_info['old_id']
                folder = zona_info['new_folder_name']
                match = re.match(r'^(\d+)_', folder)
                zone_id = int(match.group(1)) if match else old_id
                parser.set_context(area_id, region_id, zone_id)
                path_zona = CAMINHO_NOVO_MUNDO / area_key / region_key / folder
                os.makedirs(path_zona, exist_ok=True)
                
                print(f"   Processando {folder:<30}...", end="\r")
                f_wld = file_index['wld'].get(old_id)
                f_mob = file_index['mob'].get(old_id)
                f_obj = file_index['obj'].get(old_id)
                f_zon = file_index['zon'].get(old_id)

                if f_wld and parser.load_file(f_wld):
                    with open(path_zona / "rooms.yaml", 'w', encoding='utf-8') as f:
                        yaml.dump(parser.parse_rooms(), f, default_flow_style=False, allow_unicode=True)
                if f_mob and parser.load_file(f_mob):
                    with open(path_zona / "mobs.yaml", 'w', encoding='utf-8') as f:
                        yaml.dump(parser.parse_mobs(), f, default_flow_style=False, allow_unicode=True)
                if f_obj and parser.load_file(f_obj):
                    with open(path_zona / "items.yaml", 'w', encoding='utf-8') as f:
                        yaml.dump(parser.parse_objs(), f, default_flow_style=False, allow_unicode=True)
                if f_zon and parser.load_file(f_zon):
                    resets = parser.parse_zone_resets()
                    if resets:
                        with open(path_zona / "resets.yaml", 'w', encoding='utf-8') as f:
                            yaml.dump(resets, f, default_flow_style=False, allow_unicode=True)
                
                prefix = f"{area_id:02d}{region_id:02d}{zone_id:03d}"
                with open(path_zona / "manifest.yaml", 'w', encoding='utf-8') as f:
                    yaml.dump({"zone_id": f"zone_{old_id}", "vnum_prefix": QuotedString(prefix)}, f)

    print("\n✨ UNIVERSO V16 REESCRITO COM 12 DÍGITOS.")

if __name__ == "__main__":
    transmutar_mundo_v16()