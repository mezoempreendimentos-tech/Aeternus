import yaml
import os
import logging
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CAMINHO_ZONAS = PROJECT_ROOT / "data" / "world" / "zones"
LOG_FILE = SCRIPT_DIR / "linker.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s', encoding='utf-8', filemode='w')

class QuotedString(str): pass
def quoted_string_presenter(dumper, data): return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")
def multiline_presenter(dumper, data):
    if len(data.splitlines()) > 1: return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)
yaml.add_representer(QuotedString, quoted_string_presenter)
yaml.add_representer(str, multiline_presenter)

def criar_indice_global():
    print("📖 Criando Índice Global de Referência (12-digits)...")
    index = {}
    arquivos = list(CAMINHO_ZONAS.rglob("rooms.yaml"))
    
    for arq in arquivos:
        try:
            with open(arq, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if not data: continue
                for sala in data:
                    vnum_global = str(sala.get('vnum'))
                    # Tenta extrair ID Local
                    # Como o novo formato tem 12 digitos, os ultimos 5 são o local
                    try: id_local = int(vnum_global[-5:])
                    except: continue
                    index[id_local] = vnum_global
        except: pass
    return index

def corrigir_conexoes():
    print("🔗 [UTILS] LINKER V4 RODANDO...")
    global_map = criar_indice_global()
    if not global_map: return

    links_corrigidos = 0
    arquivos_salas = list(CAMINHO_ZONAS.rglob("rooms.yaml"))
    
    for arq in arquivos_salas:
        modificado = False
        dados_arquivo = []
        try:
            with open(arq, 'r', encoding='utf-8') as f: dados_arquivo = yaml.safe_load(f)
        except: continue
        if not dados_arquivo: continue

        for sala in dados_arquivo:
            sala['vnum'] = QuotedString(sala['vnum'])
            if 'exits' not in sala: continue
            for direcao, info in sala['exits'].items():
                target_atual = str(info.get('target_vnum'))
                
                try: id_local_alvo = int(target_atual[-5:]) # ATUALIZADO PARA 5 DÍGITOS
                except: continue

                if id_local_alvo in global_map:
                    novo_target_real = global_map[id_local_alvo]
                    if target_atual != novo_target_real:
                        info['target_vnum'] = QuotedString(novo_target_real)
                        modificado = True
                        links_corrigidos += 1
                    else:
                        info['target_vnum'] = QuotedString(target_atual)

        if modificado:
            with open(arq, 'w', encoding='utf-8') as f:
                yaml.dump(dados_arquivo, f, default_flow_style=False, allow_unicode=True)
    print(f"✨ Links reparados: {links_corrigidos}")

if __name__ == "__main__":
    corrigir_conexoes()