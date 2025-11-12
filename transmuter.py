import os
import re
import yaml
import sys
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================
CAMINHO_LEGADO = Path("legacy_code/lib") 
ARQUIVO_ATLAS = Path("atlas_map.yaml")
CAMINHO_NOVO_MUNDO = Path("data/world/zones")

# Configuração YAML
def str_presenter(dumper, data):
    if len(data.splitlines()) > 1:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)
yaml.add_representer(str, str_presenter)

# ==============================================================================
# FERRAMENTAS DE CURA
# ==============================================================================
def corrigir_mojibake(texto):
    """
    Tenta consertar texto quebrado (ex: 'A PraÃ§a' -> 'A Praça').
    Lógica: O texto foi salvo como UTF-8 mas aberto como CP1252/Latin-1.
    """
    if not texto: return ""
    try:
        # O passo mágico: Reverte para bytes usando a codificação "errada" (cp1252)
        # e tenta ler de novo como a codificação "certa" (utf-8).
        return texto.encode('cp1252').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Se falhar, retorna o original (pode já estar certo ou muito quebrado)
        return texto

def limpar_texto(texto):
    if not texto: return ""
    texto = corrigir_mojibake(texto)
    return texto.strip().replace('\r', '')

# ==============================================================================
# PARSER ROBUSTO
# ==============================================================================
class LegacyParser:
    def __init__(self):
        self.buffer = []
        self.idx = 0
        self.filename = ""

    def load_file(self, filepath):
        self.filename = filepath.name
        if not filepath.exists():
            print(f"   ⚠️ Arquivo não encontrado: {filepath}")
            return False
        
        # Tentativa agressiva de leitura
        try:
            # Abrimos como Latin-1 (o mais comum para MUDs antigos)
            # Isso garante que o arquivo ABRA, mesmo com caracteres estranhos.
            with open(filepath, 'r', encoding='latin-1', errors='replace') as f:
                raw = f.read()
                self.buffer = raw.splitlines()
                self.idx = 0
                return True
        except Exception as e:
            print(f"   💀 Erro fatal lendo {filepath}: {e}")
            return False

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
            line = self.buffer[self.idx] # Sem strip para manter formatação
            self.idx += 1
            
            # Remove o ~ e termina
            if '~' in line:
                clean_part = limpar_texto(line.split('~')[0])
                lines.append(clean_part)
                return "\n".join(lines).strip()
            
            lines.append(limpar_texto(line))
        return ""

    # --- PARSERS (Com Logs de Debug) ---
    def parse_rooms(self):
        rooms = []
        count = 0
        while True:
            line = self.get_next_line()
            if not line or line == '$': break
            
            if line.startswith('#'):
                vnum = line[1:]
                name_line = self.get_next_line()
                name = self.read_string(name_line)
                desc = self.read_string()
                self.get_next_line() # Skip flags/sector
                
                # Debug visual para vermos se está corrigindo
                if count < 3: 
                    print(f"      🔎 [DEBUG] Sala #{vnum}: {name}")
                
                room = {"vnum": vnum, "name": name, "description": desc, "exits": {}}
                
                # Saídas
                while True:
                    sub = self.get_next_line()
                    if not sub or sub == 'S': break
                    if sub.startswith('D') and sub[1].isdigit():
                        dir_code = int(sub[1])
                        dir_map = {0: 'north', 1: 'east', 2: 'south', 3: 'west', 4: 'up', 5: 'down'}
                        self.read_string() # Descrição da porta
                        keyword = self.get_next_line()
                        flags_line = self.get_next_line()
                        
                        if flags_line and dir_code in dir_map:
                            parts = flags_line.split()
                            if len(parts) >= 2:
                                target = parts[-1]
                                room['exits'][dir_map[dir_code]] = {"target_vnum": target}
                    elif sub == 'E':
                        self.read_string(self.get_next_line())
                        self.read_string()
                
                rooms.append(room)
                count += 1
        return rooms

    def parse_mobs(self):
        mobs = []
        while True:
            line = self.get_next_line()
            if not line or line == '$': break
            if line.startswith('#'):
                vnum = line[1:]
                keys = self.read_string(self.get_next_line())
                short = self.read_string(self.get_next_line())
                long = self.read_string()
                look = self.read_string()
                
                # Skip stats loop
                while self.idx < len(self.buffer):
                    peek = self.buffer[self.idx].strip()
                    if peek.startswith('#') or peek == '$': break
                    self.idx += 1
                
                mobs.append({"vnum": vnum, "name": short, "keywords": keys.split(), "description": look})
        return mobs

    def parse_objs(self):
        objs = []
        while True:
            line = self.get_next_line()
            if not line or line == '$': break
            if line.startswith('#'):
                vnum = line[1:]
                keys = self.read_string(self.get_next_line())
                short = self.read_string(self.get_next_line())
                long = self.read_string()
                action = self.read_string()
                
                while self.idx < len(self.buffer):
                    peek = self.buffer[self.idx].strip()
                    if peek.startswith('#') or peek == '$': break
                    self.idx += 1
                
                objs.append({"vnum": vnum, "name": short, "keywords": keys.split(), "description": long})
        return objs

# ==============================================================================
# EXECUÇÃO
# ==============================================================================
def transmutar_mundo_v4():
    print("🩺 INICIANDO DIAGNÓSTICO E TRANSMUTAÇÃO V4...")
    
    if not ARQUIVO_ATLAS.exists():
        print("❌ Atlas não encontrado.")
        return

    with open(ARQUIVO_ATLAS, 'r', encoding='utf-8') as f:
        atlas = yaml.safe_load(f)

    parser = LegacyParser()
    total_ok = 0
    
    for area_name, regioes in atlas.items():
        if area_name == "99_nao_mapeado": continue

        for regiao_name, zonas in regioes.items():
            for zona_info in zonas:
                old_id = zona_info['old_id']
                path_zona = CAMINHO_NOVO_MUNDO / area_name / regiao_name / zona_info['new_folder_name']
                os.makedirs(path_zona, exist_ok=True)
                
                print(f"\n📂 Processando Zona #{old_id}...")

                # 1. Convertendo Salas (Com Debug)
                wld_file = CAMINHO_LEGADO / "world" / "wld" / f"{old_id}.wld"
                if parser.load_file(wld_file):
                    rooms = parser.parse_rooms()
                    if rooms:
                        with open(path_zona / "rooms.yaml", 'w', encoding='utf-8') as f:
                            yaml.dump(rooms, f, default_flow_style=False, allow_unicode=True)
                        print(f"   ✅ {len(rooms)} salas salvas.")
                        total_ok += 1
                    else:
                        print("   ⚠️ Arquivo lido, mas nenhuma sala encontrada (Parser falhou?)")
                
                # 2. Convertendo Mobs
                mob_file = CAMINHO_LEGADO / "world" / "mob" / f"{old_id}.mob"
                if parser.load_file(mob_file):
                    mobs = parser.parse_mobs()
                    if mobs:
                        with open(path_zona / "mobs.yaml", 'w', encoding='utf-8') as f:
                            yaml.dump(mobs, f, default_flow_style=False, allow_unicode=True)
                        print(f"   ✅ {len(mobs)} mobs salvos.")

                # 3. Convertendo Items
                obj_file = CAMINHO_LEGADO / "world" / "obj" / f"{old_id}.obj"
                if parser.load_file(obj_file):
                    objs = parser.parse_objs()
                    if objs:
                        with open(path_zona / "items.yaml", 'w', encoding='utf-8') as f:
                            yaml.dump(objs, f, default_flow_style=False, allow_unicode=True)
                        print(f"   ✅ {len(objs)} itens salvos.")

                # 4. Manifest simples
                with open(path_zona / "manifest.yaml", 'w', encoding='utf-8') as f:
                    yaml.dump({"zone_id": f"zone_{old_id}", "legacy_id": old_id}, f)

    if total_ok > 0:
        print("\n✨ SUCESSO! Se você viu nomes corrigidos no log (sem Ã©), funcionou.")
    else:
        print("\n💀 FALHA TOTAL. Nenhum arquivo produziu dados válidos.")

if __name__ == "__main__":
    transmutar_mundo_v4()