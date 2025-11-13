import os
import yaml
from pathlib import Path

# CONFIGURAÇÃO DE PASTA
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CAMINHO_MUNDO = PROJECT_ROOT / "data" / "world" / "zones"

# ... (O RESTO DO CÓDIGO É IGUAL AO ANTERIOR - CURAS, str_presenter, curar_string, etc) ...
# (Certifique-se de copiar as funções e dicionários do healer.py original para aqui)

# -- APENAS PARA GARANTIR, COLE O RESTANTE ABAIXO: --
CURAS = {
    'Ã¡': 'á', 'Ã ': 'à', 'Ã¢': 'â', 'Ã£': 'ã', 'Ã¤': 'ä',
    'Ã‰': 'É', 'Ã©': 'é', 'Ã¨': 'è', 'Ãª': 'ê', 'Ã«': 'ë',
    'Ã ': 'Í', 'Ã­': 'í', 'Ã¬': 'ì', 'Ã®': 'î', 'Ã¯': 'ï',
    'Ã“': 'Ó', 'Ã³': 'ó', 'Ã²': 'ò', 'Ã´': 'ô', 'Ãµ': 'õ', 'Ã¶': 'ö',
    'Ãš': 'Ú', 'Ãº': 'ú', 'Ã¹': 'ù', 'Ã»': 'û', 'Ã¼': 'ü',
    'Ã‡': 'Ç', 'Ã§': 'ç', 'Ã‘': 'Ñ', 'Ã±': 'ñ',
    'Â': '', '\\r': '',
}

def str_presenter(dumper, data):
    if len(data.splitlines()) > 1:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)
yaml.add_representer(str, str_presenter)

def curar_string(texto):
    if not isinstance(texto, str): return texto, False
    novo_texto = texto
    mudou = False
    for ferida, remedio in CURAS.items():
        if ferida in novo_texto:
            novo_texto = novo_texto.replace(ferida, remedio)
            mudou = True
    return novo_texto, mudou

def percorrer_dados(dados):
    modificado_total = False
    if isinstance(dados, dict):
        for k, v in dados.items():
            if isinstance(v, str):
                novo_v, mudou = curar_string(v)
                if mudou: dados[k] = novo_v; modificado_total = True
            elif isinstance(v, (dict, list)):
                if percorrer_dados(v): modificado_total = True
    elif isinstance(dados, list):
        for i, v in enumerate(dados):
            if isinstance(v, str):
                novo_v, mudou = curar_string(v)
                if mudou: dados[i] = novo_v; modificado_total = True
            elif isinstance(v, (dict, list)):
                if percorrer_dados(v): modificado_total = True
    return modificado_total

def iniciar_tratamento():
    print(f"⚕️  [UTILS] HEALER EXAMINANDO MUNDO EM: {CAMINHO_MUNDO}")
    arquivos_curados = 0
    for arquivo in CAMINHO_MUNDO.rglob("*.yaml"):
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = yaml.safe_load(f)
            if not dados: continue
            if percorrer_dados(dados):
                with open(arquivo, 'w', encoding='utf-8') as f:
                    yaml.dump(dados, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                print(f"   ✨ Curado: {arquivo.name}")
                arquivos_curados += 1
        except: pass
    print(f"FIM. {arquivos_curados} arquivos curados.")

if __name__ == "__main__":
    iniciar_tratamento()