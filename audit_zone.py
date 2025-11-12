import sys
import yaml
import os
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÃO VISUAL
# ==============================================================================
class Cor:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def carregar_yaml(caminho):
    if not caminho.exists():
        return {} # Retorna vazio se não existir (algumas zonas não têm mobs/items)
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"{Cor.FAIL}   CRÍTICO: Falha ao ler {caminho.name}: {e}{Cor.RESET}")
        return None

def encontrar_pasta_zona(zone_id_alvo):
    """Caça a pasta correta procurando no manifest.yaml"""
    raiz = Path("data/world/zones")
    print(f"{Cor.BLUE}🔍 Procurando pelos arquivos da Zona Antiga #{zone_id_alvo}...{Cor.RESET}")
    
    for path in raiz.rglob("manifest.yaml"):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                dados = yaml.safe_load(f)
                if str(dados.get('legacy_id')) == str(zone_id_alvo):
                    return path.parent
        except:
            continue
    return None

def auditar_zona(zone_id):
    pasta = encontrar_pasta_zona(zone_id)
    
    if not pasta:
        print(f"{Cor.FAIL}❌ Zona #{zone_id} não encontrada nos arquivos convertidos.{Cor.RESET}")
        print("   Verifique se rodou o transmuter ou se o ID está correto.")
        return

    print(f"{Cor.GREEN}✅ Zona Localizada: {pasta}{Cor.RESET}")
    print("="*60)

    # 1. Carregar Dados
    rooms = carregar_yaml(pasta / "rooms.yaml") or []
    mobs = carregar_yaml(pasta / "mobs.yaml") or []
    items = carregar_yaml(pasta / "items.yaml") or []
    scripts = carregar_yaml(pasta / "scripts.yaml") or []
    resets = carregar_yaml(pasta / "resets.yaml") or []

    # Indexar para busca rápida (Dicionários VNUM -> Objeto)
    db_rooms = {str(r['vnum']): r for r in rooms}
    db_mobs = {str(m['vnum']): m for m in mobs}
    db_items = {str(i['vnum']): i for i in items}
    db_scripts = {str(s['vnum']): s for s in scripts}

    print(f"📊 Censo da Zona:")
    print(f"   🏠 Salas:    {len(rooms)}")
    print(f"   👹 Mobs:     {len(mobs)}")
    print(f"   ⚔️  Itens:    {len(items)}")
    print(f"   📜 Scripts:  {len(scripts)}")
    print(f"   ⚙️  Resets:   {len(resets)}")
    print("-" * 60)

    erros = 0
    avisos = 0

    # 2. Validar Resets (A parte crucial para Triggers e População)
    print(f"{Cor.HEADER}🕵️  Validando Integridade dos Resets & Triggers...{Cor.RESET}")
    
    for i, cmd in enumerate(resets):
        tipo = cmd.get('type')
        
        # Checar Mobs
        if tipo == 'load_mob':
            mob_id = str(cmd.get('mob_vnum'))
            room_id = str(cmd.get('room_vnum'))
            if mob_id not in db_mobs:
                print(f"   {Cor.FAIL}💀 Reset #{i}: Tenta carregar Mob {mob_id} (INEXISTENTE) na sala {room_id}.{Cor.RESET}")
                erros += 1
            if room_id not in db_rooms:
                print(f"   {Cor.WARNING}⚠️  Reset #{i}: Tenta carregar Mob {mob_id} na sala {room_id} (SALA DE OUTRA ZONA?){Cor.RESET}")
                avisos += 1

        # Checar Triggers (O que você pediu!)
        elif tipo == 'attach_trigger':
            trig_id = str(cmd.get('trigger_vnum'))
            target_id = str(cmd.get('target_vnum')) # Pode ser sala, mob ou obj
            
            if trig_id not in db_scripts:
                print(f"   {Cor.FAIL}💀 Reset #{i}: Tenta anexar Trigger {trig_id} (INEXISTENTE) ao alvo {target_id}.{Cor.RESET}")
                erros += 1
            else:
                script = db_scripts[trig_id]
                nome_script = script.get('name', 'Sem Nome')
                print(f"   {Cor.CYAN}⚡ Link Confirmado: Trigger {trig_id} ('{nome_script}') -> Alvo {target_id}{Cor.RESET}")

    # 3. Validar Scripts
    if scripts:
        print("-" * 60)
        print(f"{Cor.HEADER}📜  Amostragem de Scripts (Triggers):{Cor.RESET}")
        for s in scripts[:3]: # Mostra os 3 primeiros para não poluir
            print(f"   ID {s['vnum']} | Tipo: {s['attach_type']} | Nome: {s['name']}")
            # print(f"   Conteúdo: {s['script_code'][:50]}...") # Descomente para ver o código

    print("="*60)
    if erros == 0:
        print(f"{Cor.GREEN}✨ AUDITORIA APROVADA: A estrutura lógica parece sólida.{Cor.RESET}")
        if avisos > 0: print(f"   (Com {avisos} avisos de referências externas)")
    else:
        print(f"{Cor.FAIL}❌ AUDITORIA REPROVADA: Encontrados {erros} erros graves de integridade.{Cor.RESET}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python audit_zone.py <ID_DA_ZONA>")
        print("Exemplo: python audit_zone.py 10")
    else:
        auditar_zona(sys.argv[1])