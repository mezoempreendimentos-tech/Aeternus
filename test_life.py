import yaml
import sys
from pathlib import Path

# Adiciona a pasta atual ao path para importar os módulos do 'aeternus'
sys.path.append(str(Path(".")))

from aeternus.game.objects.room import Room

def carregar_primeira_sala():
    arquivo_yaml = Path("data/world/zones/00_plano_etereo/00_limbo/00_centro/rooms.yaml")
    
    print(f"🔍 [SISTEMA] Procurando o pergaminho em: {arquivo_yaml}")
    
    if not arquivo_yaml.exists():
        print("❌ [ERRO] O arquivo não existe. Você criou as pastas?")
        return

    with open(arquivo_yaml, 'r', encoding='utf-8') as f:
        dados = yaml.safe_load(f)
        
    # Pegamos a primeira sala da lista
    dados_sala = dados[0]
    
    # --- O MOMENTO DA CRIAÇÃO ---
    # Instanciamos a classe Python usando dados do YAML
    nova_sala = Room(vnum=dados_sala['vnum'], name=dados_sala['name'])
    nova_sala.description = dados_sala['description']
    
    # Simulando o carregamento de saídas
    if 'exits' in dados_sala:
        for direcao, info in dados_sala['exits'].items():
            nova_sala.add_exit(direcao, info['target_vnum'])

    # --- A REVELAÇÃO ---
    print("\n" + "="*60)
    print("✨ SUCESSO! O Python materializou a seguinte realidade:")
    print("="*60)
    # Aqui chamamos o método que criamos no room.py anteriormente
    print(nova_sala.get_description_for(looker=None))
    print("="*60)
    print(f"🧠 Memória: Objeto <Room> criado com UUID: {nova_sala.uuid}")

if __name__ == "__main__":
    try:
        carregar_primeira_sala()
    except ImportError:
        print("❌ [ERRO] Não encontrei o módulo 'aeternus'. Execute o script da raiz do projeto.")
    except Exception as e:
        print(f"💀 [FATAL] O ritual falhou: {e}")