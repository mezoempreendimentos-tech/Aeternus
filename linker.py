import yaml
import os
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================
ARQUIVO_ATLAS = Path("atlas_map.yaml")
CAMINHO_ZONAS = Path("data/world/zones")

def carregar_atlas():
    """
    Cria um mapa: ID_ANTIGO_ZONA (int) -> PREFIXO_NOVO (str)
    """
    if not ARQUIVO_ATLAS.exists():
        print("❌ Atlas não encontrado.")
        return {}

    mapa_zonas = {}
    
    with open(ARQUIVO_ATLAS, 'r', encoding='utf-8') as f:
        atlas = yaml.safe_load(f)

    for area_key, regioes in atlas.items():
        if area_key == "99_nao_mapeado": continue
        # Extrai AA (01)
        area_id = int(area_key.split('_')[0])

        for region_key, zonas in regioes.items():
            # Extrai RR (01)
            region_id = int(region_key.split('_')[0])
            
            for zona in zonas:
                old_id = zona['old_id'] # Ex: 10
                
                # Tenta extrair ZZZ do nome da pasta (010_midgaard -> 10)
                folder = zona['new_folder_name']
                try:
                    zone_id_novo = int(folder.split('_')[0])
                except:
                    zone_id_novo = old_id

                # Monta o prefixo: AA RR ZZZ
                prefixo = f"{area_id:02d}{region_id:02d}{zone_id_novo:03d}"
                mapa_zonas[old_id] = prefixo
                
    return mapa_zonas

def corrigir_conexoes():
    print("🔗 INICIANDO PROCESSO DE LINKAGEM GLOBAL...")
    
    # 1. Entender o Mapa
    mapa_prefixos = carregar_atlas()
    print(f"🗺️  Mapeadas {len(mapa_prefixos)} zonas do mundo antigo.")

    # 2. Carregar todas as salas para validar links
    print("📂 Indexando todas as salas existentes...")
    salas_existentes = set()
    arquivos_salas = list(CAMINHO_ZONAS.rglob("rooms.yaml"))
    
    for arq in arquivos_salas:
        try:
            with open(arq, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data:
                    for sala in data:
                        salas_existentes.add(str(sala['vnum']))
        except: pass

    print(f"✅ Indexadas {len(salas_existentes)} salas reais.")

    # 3. Corrigir Links Quebrados
    links_corrigidos = 0
    
    for arq in arquivos_salas:
        modificado = False
        dados_arquivo = []
        
        try:
            with open(arq, 'r', encoding='utf-8') as f:
                dados_arquivo = yaml.safe_load(f)
        except: continue

        if not dados_arquivo: continue

        for sala in dados_arquivo:
            if 'exits' not in sala: continue
            
            for direcao, info in sala['exits'].items():
                target_atual = str(info.get('target_vnum'))
                
                # Se o link já funciona, ignora
                if target_atual in salas_existentes:
                    continue
                
                # SE O LINK ESTÁ QUEBRADO: Tenta Deduzir
                # O target_atual gerado pelo transmutador v7 provavelmente está errado
                # porque usou o prefixo da zona ATUAL para um ID de OUTRA zona.
                
                # Vamos tentar recuperar o ID Local Antigo.
                # Como o VNUM V7 é AA RR ZZZ RRRR, os últimos 4 são o ID local.
                try:
                    id_local_antigo = int(target_atual[-4:]) # Pega os ultimos 4 digitos
                except:
                    continue

                # Regra do CircleMUD: A zona é ID // 100
                # Ex: Se quero ir para sala 4001, a zona é 40.
                zona_alvo_antiga = id_local_antigo // 100
                
                # Busca o prefixo correto dessa zona no nosso Atlas
                if zona_alvo_antiga in mapa_prefixos:
                    prefixo_correto = mapa_prefixos[zona_alvo_antiga]
                    novo_target = f"{prefixo_correto}{id_local_antigo:04d}"
                    
                    # Verifica se essa correção existe de verdade
                    if novo_target in salas_existentes:
                        print(f"🔧 Corrigindo {sala['vnum']} ({direcao}): {target_atual} -> {novo_target}")
                        sala['exits'][direcao]['target_vnum'] = novo_target
                        modificado = True
                        links_corrigidos += 1
                    else:
                        # print(f"⚠️ Link morto sem solução: {sala['vnum']} -> {id_local_antigo} (Zona {zona_alvo_antiga} não tem sala)")
                        pass

        if modificado:
            with open(arq, 'w', encoding='utf-8') as f:
                yaml.dump(dados_arquivo, f, default_flow_style=False, allow_unicode=True)

    print("\n" + "="*60)
    print(f"✨ SUCESSO: {links_corrigidos} portais interdimensionais foram reparados.")
    print("="*60)

if __name__ == "__main__":
    corrigir_conexoes()