import os
import yaml
from pathlib import Path

# CONFIGURAÇÃO
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
LEGACY_WLD = PROJECT_ROOT / "legacy_code" / "lib" / "world" / "wld"
NEW_ZONES = PROJECT_ROOT / "data" / "world" / "zones"

def contar_salas_legado(arquivo):
    """Conta linhas começando com #NUMERO"""
    count = 0
    try:
        with open(arquivo, 'r', encoding='latin-1', errors='ignore') as f:
            for line in f:
                if line.startswith('#') and len(line) > 1 and line[1].isdigit():
                    count += 1
    except: pass
    return count

def contar_salas_novo(arquivo):
    """Lê o YAML e conta itens na lista"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if isinstance(data, list):
                return len(data)
            return 0
    except: return 0

def realizar_censo():
    print("\n📊 CENSO V2: FORÇA BRUTA")
    print(f"   Varrendo Legado: {LEGACY_WLD}")
    print(f"   Varrendo Novo:   {NEW_ZONES}")
    print("-" * 70)

    # 1. Indexar o Mundo Novo primeiro
    print("🔍 Indexando zonas novas...")
    mapa_novo = {} # legacy_id -> qtd_salas
    
    manifests = list(NEW_ZONES.rglob("manifest.yaml"))
    print(f"   Encontrados {len(manifests)} arquivos de manifesto.")

    for manifest in manifests:
        try:
            with open(manifest, 'r', encoding='utf-8') as f:
                meta = yaml.safe_load(f)
                
            # Tenta pegar o ID antigo de várias formas
            legacy_id = meta.get('legacy_id')
            if legacy_id is None:
                # Tenta extrair do zone_id "zone_10"
                zid = str(meta.get('zone_id', ''))
                if '_' in zid:
                    legacy_id = int(zid.split('_')[1])
            
            legacy_id = int(legacy_id)
            
            # Conta as salas
            rooms_file = manifest.parent / "rooms.yaml"
            qtd = 0
            if rooms_file.exists():
                qtd = contar_salas_novo(rooms_file)
            
            mapa_novo[legacy_id] = qtd
            
        except Exception as e:
            # print(f"   Erro lendo {manifest}: {e}")
            pass

    # 2. Comparar com o Legado
    print("🔍 Comparando com o Legado...")
    print(f"{'ID':<6} | {'ARQUIVO':<15} | {'ANTIGO':<8} | {'NOVO':<8} | {'STATUS'}")
    print("-" * 70)

    total_antigo = 0
    total_novo = 0
    
    arquivos_wld = sorted(list(LEGACY_WLD.glob("*.wld")), key=lambda x: int(x.stem) if x.stem.isdigit() else 99999)

    for wld in arquivos_wld:
        if not wld.stem.isdigit(): continue
        
        zone_id = int(wld.stem)
        qtd_antiga = contar_salas_legado(wld)
        qtd_nova = mapa_novo.get(zone_id, 0)

        total_antigo += qtd_antiga
        total_novo += qtd_nova
        
        status = "✅ OK"
        if qtd_nova == 0: status = "💀 ZERO"
        elif qtd_nova < qtd_antiga: status = f"⚠️ -{qtd_antiga - qtd_nova}"
        elif qtd_nova > qtd_antiga: status = f"📈 +{qtd_nova - qtd_antiga}"
        
        # Só mostra se houver discrepância ou para debug
        # Se quiser ver tudo, remova o if abaixo
        if status != "✅ OK" or qtd_antiga > 0:
             print(f"{zone_id:<6} | {wld.name:<15} | {qtd_antiga:<8} | {qtd_nova:<8} | {status}")

    print("-" * 70)
    print(f"TOTAL ANTIGO: {total_antigo}")
    print(f"TOTAL NOVO:   {total_novo}")
    print("-" * 70)

if __name__ == "__main__":
    realizar_censo()