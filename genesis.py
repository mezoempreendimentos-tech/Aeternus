import re
import yaml
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================
ARQUIVO_DESCRICOES = Path("areas_descr")  # O arquivo que você enviou
ARQUIVO_SAIDA = Path("atlas_map.yaml")

# ==============================================================================
# O ESCRIBA
# ==============================================================================
def parse_areas_file():
    if not ARQUIVO_DESCRICOES.exists():
        print(f"❌ [ERRO] O arquivo '{ARQUIVO_DESCRICOES}' não foi encontrado na raiz.")
        return {}

    print(f"📜 Lendo pergaminhos de: {ARQUIVO_DESCRICOES}...")
    
    # Dicionário para armazenar as zonas encontradas
    # Estrutura: { id: "Nome da Zona" }
    zonas_encontradas = {}
    
    with open(ARQUIVO_DESCRICOES, 'r', encoding='latin-1', errors='ignore') as f:
        content = f.readlines()

    i = 0
    while i < len(content):
        line = content[i].strip()
        
        # Procura o padrão: ==> 113.zon <==
        match = re.search(r"==> (\d+)\.zon <==", line)
        if match:
            zone_id = int(match.group(1))
            
            # A próxima linha geralmente é o ID (#113), pulamos
            i += 1 
            
            # A linha seguinte é o nome (Bhogavati...~)
            if i < len(content):
                raw_name = content[i].strip()
                # Remove o ~ do final e aspas extras se houver
                clean_name = raw_name.replace('~', '').strip().strip('"')
                
                zonas_encontradas[zone_id] = clean_name
                print(f"   ✅ Mapeado: [{zone_id}] {clean_name}")
        
        i += 1
        
    return zonas_encontradas

def gerar_atlas(zonas):
    atlas = {}
    
    print(f"\n🗺️  Organizando {len(zonas)} territórios no Atlas AARRZZ...")

    for zid, nome in zonas.items():
        # --- LÓGICA DE AGRUPAMENTO (HEURÍSTICA) ---
        # Tentamos adivinhar a região baseada no número, mas o NOME agora está correto.
        
        area = "99_plano_desconhecido"
        regiao = "00_limbo"
        
        if zid < 50:
            area = "01_plano_material"
            regiao = "01_reino_central"  # Midgaard, Cidades Iniciais
        elif 50 <= zid < 100:
            area = "01_plano_material"
            regiao = "02_reino_thalos"   # Thalos, Florestas próximas
        elif 100 <= zid < 200:
            area = "02_terras_selvagens"
            regiao = "01_oriente"        # Bhogavati, etc.
        elif zid >= 200:
            area = "03_planos_exteriores"
            regiao = "01_cosmos"

        # Cria a estrutura se não existir
        if area not in atlas:
            atlas[area] = {}
        if regiao not in atlas[area]:
            atlas[area][regiao] = []
            
        # Formata o nome da pasta para ser amigável ao sistema (snake_case)
        # Ex: "A Cidade de Thalos" -> "cidade_thalos"
        nome_pasta = nome.lower()
        nome_pasta = re.sub(r'[àáâãäå]', 'a', nome_pasta)
        nome_pasta = re.sub(r'[èéêë]', 'e', nome_pasta)
        nome_pasta = re.sub(r'[ìíîï]', 'i', nome_pasta)
        nome_pasta = re.sub(r'[òóôõö]', 'o', nome_pasta)
        nome_pasta = re.sub(r'[ùúûü]', 'u', nome_pasta)
        nome_pasta = re.sub(r'[ç]', 'c', nome_pasta)
        nome_pasta = re.sub(r'[^a-z0-9\s]', '', nome_pasta) # Remove simbolos
        nome_pasta = re.sub(r'\s+', '_', nome_pasta)       # Espaço -> _
        
        entrada = {
            "old_id": zid,
            "original_name": nome,
            "new_folder_name": nome_pasta
        }
        
        atlas[area][regiao].append(entrada)

    # Salva o arquivo
    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
        yaml.dump(atlas, f, sort_keys=True, allow_unicode=True, default_flow_style=False)

    print("="*60)
    print(f"✨ SUCESSO! O Atlas foi escrito em: {ARQUIVO_SAIDA}")
    print("="*60)
    print("👉 AGORA: Abra o arquivo atlas_map.yaml e ajuste as regiões conforme seu desejo.")
    print("   Quando estiver satisfeito, me avise para iniciarmos a TRANSMUTAÇÃO (Conversão).")

if __name__ == "__main__":
    zonas = parse_areas_file()
    if zonas:
        gerar_atlas(zonas)