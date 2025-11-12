import re
import yaml
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================
ARQUIVO_ENTRADA = Path("areas_descr")
ARQUIVO_SAIDA = Path("atlas_map.yaml")

def transmutar_nome_pasta(nome_sujo):
    """Transforma 'Caverna do Dragão~' em 'caverna_do_dragao'"""
    # Remove acentos e caracteres especiais
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
    
    # Remove tudo que não for letra, número ou espaço
    nome = re.sub(r'[^a-z0-9\s]', '', nome)
    # Substitui espaços por underscores
    nome = re.sub(r'\s+', '_', nome)
    return nome

def mapear_verdade():
    if not ARQUIVO_ENTRADA.exists():
        print(f"❌ [ERRO] O grimório '{ARQUIVO_ENTRADA}' não está aqui. Onde você o escondeu?")
        return

    print(f"🔍 Lendo a verdade em: {ARQUIVO_ENTRADA}...")
    
    with open(ARQUIVO_ENTRADA, 'r', encoding='latin-1', errors='ignore') as f:
        linhas = f.readlines()

    atlas = {}
    zona_atual = None
    
    # Estado da Máquina de Leitura
    # 0 = Procurando Cabeçalho (==> 123.zon <==)
    # 1 = Procurando Nome (Ignorando #123, buscando algo com ~)
    estado = 0 

    count = 0

    for linha in linhas:
        linha = linha.strip()
        if not linha: continue

        # Fase 1: Encontrar o início de um bloco
        if estado == 0:
            match = re.search(r"==> (\d+)\.zon <==", linha)
            if match:
                zona_atual = int(match.group(1))
                estado = 1 # Agora estamos caçando o nome
                continue

        # Fase 2: Encontrar o nome (linha que termina com ~)
        if estado == 1:
            if linha.startswith("#"): 
                continue # Pula o ID repetido
            
            if "~" in linha:
                # ACHAMOS!
                nome_bruto = linha.replace("~", "").strip()
                nome_pasta = transmutar_nome_pasta(nome_bruto)
                
                # Lógica de Agrupamento (Chute inicial para você organizar depois)
                area = "99_nao_mapeado"
                regiao = "00_limbo"
                
                if zona_atual < 100:
                    area = "01_plano_material"
                    regiao = "01_reino_vitalia"
                elif zona_atual < 200:
                    area = "01_plano_material"
                    regiao = "02_terras_selvagens"
                else:
                    area = "02_planos_exteriores"
                    regiao = "01_cosmos"

                # Inserir no Atlas
                if area not in atlas: atlas[area] = {}
                if regiao not in atlas[area]: atlas[area][regiao] = []

                entry = {
                    "old_id": zona_atual,
                    "original_name": nome_bruto,
                    "new_folder_name": f"{zona_atual:03d}_{nome_pasta}" # Adicionei o ID no nome da pasta para facilitar
                }
                
                atlas[area][regiao].append(entry)
                print(f"   ✅ Mapeado: [{zona_atual}] {nome_bruto}")
                
                count += 1
                estado = 0 # Volta a procurar próxima zona
                zona_atual = None

    # Salvar o Atlas
    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
        yaml.dump(atlas, f, sort_keys=True, allow_unicode=True, default_flow_style=False)

    print("\n" + "="*60)
    print(f"✨ ATLAS CORRIGIDO! {count} zonas recuperadas.")
    print(f"📄 Arquivo gerado: {ARQUIVO_SAIDA}")
    print("="*60)
    print("👉 Agora abra o atlas_map.yaml. Os nomes devem ser reais (ex: 'Midgaard', 'Floresta').")
    print("👉 Se estiver bom, me avise para invocarmos o TRANSMUTADOR (Conversão Final).")

if __name__ == "__main__":
    mapear_verdade()