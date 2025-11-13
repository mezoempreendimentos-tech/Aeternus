import os
import yaml
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================
CAMINHO_MUNDO = Path("data/world/zones")

# O Grimório de Cura (Mapeamento de Erros Comuns -> Correção)
# Estes são os padrões exatos que ocorrem quando UTF-8 é lido como Latin-1
CURAS = {
    'Ã¡': 'á', 'Ã ': 'à', 'Ã¢': 'â', 'Ã£': 'ã', 'Ã¤': 'ä',
    'Ã‰': 'É', 'Ã©': 'é', 'Ã¨': 'è', 'Ãª': 'ê', 'Ã«': 'ë',
    'Ã ': 'Í', 'Ã­': 'í', 'Ã¬': 'ì', 'Ã®': 'î', 'Ã¯': 'ï',
    'Ã“': 'Ó', 'Ã³': 'ó', 'Ã²': 'ò', 'Ã´': 'ô', 'Ãµ': 'õ', 'Ã¶': 'ö',
    'Ãš': 'Ú', 'Ãº': 'ú', 'Ã¹': 'ù', 'Ã»': 'û', 'Ã¼': 'ü',
    'Ã‡': 'Ç', 'Ã§': 'ç', 'Ã‘': 'Ñ', 'Ã±': 'ñ',
    'Â': '',   # Espaço fantasma (Non-breaking space corrompido)
    'â‚¬': '€',
    'Âº': 'º', 'Â°': '°',
    'â€”': '—',
    '\r': '',  # Remove carriage return do Windows
}

# Configuração para o YAML ficar bonito (Blocos de texto com |)
def str_presenter(dumper, data):
    if len(data.splitlines()) > 1:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

# ==============================================================================
# LÓGICA DE CURA
# ==============================================================================
def curar_string(texto):
    """Aplica as substituições no texto."""
    if not isinstance(texto, str):
        return texto, False
    
    novo_texto = texto
    mudou = False
    
    for ferida, remedio in CURAS.items():
        if ferida in novo_texto:
            novo_texto = novo_texto.replace(ferida, remedio)
            mudou = True
            
    return novo_texto, mudou

def percorrer_dados(dados):
    """Percorre recursivamente dicionários e listas para curar strings."""
    modificado_total = False
    
    if isinstance(dados, dict):
        for k, v in dados.items():
            if isinstance(v, str):
                novo_v, mudou = curar_string(v)
                if mudou:
                    dados[k] = novo_v
                    modificado_total = True
            elif isinstance(v, (dict, list)):
                if percorrer_dados(v):
                    modificado_total = True
                    
    elif isinstance(dados, list):
        for i, v in enumerate(dados):
            if isinstance(v, str):
                novo_v, mudou = curar_string(v)
                if mudou:
                    dados[i] = novo_v
                    modificado_total = True
            elif isinstance(v, (dict, list)):
                if percorrer_dados(v):
                    modificado_total = True
                    
    return modificado_total

def iniciar_tratamento():
    print(f"⚕️  O CLÉRIGO ESTÁ PERCORRENDO O MUNDO EM: {CAMINHO_MUNDO}")
    print("    Procurando feridas de codificação (Mojibake)...")
    
    arquivos_curados = 0
    total_arquivos = 0
    
    # Busca todos os arquivos YAML recursivamente
    for arquivo in CAMINHO_MUNDO.rglob("*.yaml"):
        total_arquivos += 1
        try:
            # Carrega
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = yaml.safe_load(f)
            
            if not dados: continue

            # Tenta curar
            if percorrer_dados(dados):
                # Se houve cura, salva de volta
                with open(arquivo, 'w', encoding='utf-8') as f:
                    yaml.dump(dados, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                print(f"   ✨ Curado: {arquivo.name} (em {arquivo.parent.name})")
                arquivos_curados += 1
                
        except Exception as e:
            print(f"   💀 Falha ao examinar {arquivo}: {e}")

    print("\n" + "="*60)
    print(f"RELATÓRIO FINAL:")
    print(f"Arquivos examinados: {total_arquivos}")
    print(f"Arquivos curados:    {arquivos_curados}")
    
    if arquivos_curados > 0:
        print("O mundo está mais saudável agora.")
    else:
        print("Nenhuma ferida encontrada. O mundo já estava puro.")

if __name__ == "__main__":
    iniciar_tratamento()