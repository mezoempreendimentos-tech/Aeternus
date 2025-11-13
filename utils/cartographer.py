import re
import yaml
import sys
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
ARQUIVO_ENTRADA = SCRIPT_DIR / "areas_descr"
ARQUIVO_SAIDA = SCRIPT_DIR / "atlas_map.yaml"

# ==============================================================================
# LÓGICA DE LORE (A Inteligência Geográfica)
# ==============================================================================
def definir_regiao(zone_id, nome):
    """
    Define AA (Área) e RR (Região) baseado no ID e Palavras-Chave.
    Baseado no layout clássico Diku/Circle/Vitalia.
    """
    nome = nome.lower()
    
    # --- 0. SISTEMA & TESTES ---
    if zone_id < 3:
        return "00_sistema", "00_limbo"
    
    # --- 1. REINO DE MIDGAARD (O Início) ---
    # Zonas 30-39 geralmente são arredores de Midgaard
    # Zona 10 é a cidade.
    if zone_id == 10 or (30 <= zone_id <= 39):
        return "01_plano_material", "01_reino_midgaard"
    if "midgaard" in nome or "mordecai" in nome:
        return "01_plano_material", "01_reino_midgaard"

    # --- 2. AS MONTANHAS E MINAS (Norte/Oeste) ---
    # Zonas 40-49 (Moria, Gnomos, Montanhas)
    if (40 <= zone_id <= 49) or "moria" in nome or "anão" in nome or "dwarven" in nome or "mine" in nome:
        return "01_plano_material", "02_montanhas_de_ferro"

    # --- 3. O DESERTO DE THALOS (Leste/Sul) ---
    # Zonas 50-59 (New Thalos, Pirâmides, Deserto)
    if (50 <= zone_id <= 59) or "thalos" in nome or "desert" in nome or "piramide" in nome or "pyramid" in nome:
        return "01_plano_material", "03_deserto_de_thalos"

    # --- 4. A GRANDE FLORESTA (Haon-Dor) ---
    # Zonas 60-79 (Florestas, Orcs, Aranhas)
    if (60 <= zone_id <= 79) or "haon" in nome or "forest" in nome or "floresta" in nome or "elf" in nome or "orc" in nome:
        return "01_plano_material", "04_floresta_haon_dor"

    # --- 5. ALTO NÍVEL / DIVERSOS (80-199) ---
    if 80 <= zone_id <= 99:
        return "01_plano_material", "05_terras_devastadas" # Githyanki, etc
    
    if 100 <= zone_id <= 199:
        return "01_plano_material", "06_terras_distantes"

    # --- 6. PLANOS EXTERIORES (200+) ---
    if zone_id >= 200:
        if "hell" in nome or "abyss" in nome or "inferno" in nome or "hades" in nome:
            return "02_planos_exteriores", "02_planos_inferiores"
        if "olympus" in nome or "god" in nome or "heaven" in nome or "divin" in nome:
            return "02_planos_exteriores", "01_planos_superiores"
        return "02_planos_exteriores", "03_plano_astral"

    # Fallback
    return "99_nao_mapeado", "00_desconhecida"

def transmutar_nome_pasta(nome_sujo):
    nome = nome_sujo.lower()
    mapeamento = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'ñ': 'n'
    }
    for char, subst in mapeamento.items():
        nome = nome.replace(char, subst)
    
    nome = re.sub(r'[^a-z0-9\s]', '', nome)
    nome = re.sub(r'\s+', '_', nome)
    return nome

def mapear_verdade():
    if not ARQUIVO_ENTRADA.exists():
        print(f"❌ [ERRO] Arquivo '{ARQUIVO_ENTRADA}' não encontrado.")
        return

    print(f"🔍 [CARTÓGRAFO V5] Lendo pergaminhos antigos...")
    
    with open(ARQUIVO_ENTRADA, 'r', encoding='latin-1', errors='ignore') as f:
        linhas = f.readlines()

    atlas = {}
    zona_atual = None
    estado = 0 
    count = 0

    for linha in linhas:
        linha = linha.strip()
        if not linha: continue

        if estado == 0:
            match = re.search(r"==> (\d+)\.zon <==", linha)
            if match:
                zona_atual = int(match.group(1))
                estado = 1
                continue

        if estado == 1:
            if linha.startswith("#"): continue
            
            if "~" in linha:
                nome_bruto = linha.replace("~", "").strip()
                nome_pasta = transmutar_nome_pasta(nome_bruto)
                
                # --- APLICANDO A INTELIGÊNCIA GEOGRÁFICA ---
                area, regiao = definir_regiao(zona_atual, nome_bruto)
                # -------------------------------------------

                if area not in atlas: atlas[area] = {}
                if regiao not in atlas[area]: atlas[area][regiao] = []

                # Nome da pasta agora inclui ID para evitar colisão
                # Ex: 010_midgaard
                folder = f"{zona_atual:03d}_{nome_pasta}"

                entry = {
                    "old_id": zona_atual,
                    "original_name": nome_bruto,
                    "new_folder_name": folder
                }
                
                atlas[area][regiao].append(entry)
                count += 1
                
                estado = 0
                zona_atual = None

    # Salvar o Atlas Atualizado
    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
        yaml.dump(atlas, f, sort_keys=True, allow_unicode=True, default_flow_style=False)

    print(f"\n✨ ATLAS LORE-FRIENDLY GERADO! {count} zonas organizadas.")
    print(f"📄 Verifique: {ARQUIVO_SAIDA}")
    print("👉 PRÓXIMOS PASSOS (PARA APLICAR A MUDANÇA):")
    print("   1. rm -rf data/world/zones (Apagar o mundo antigo bagunçado)")
    print("   2. python utils/transmuter.py")
    print("   3. python utils/healer.py")
    print("   4. python utils/linker.py")
    print("   5. python utils/locator.py (Para pegar o novo ID da Praça)")

if __name__ == "__main__":
    mapear_verdade()