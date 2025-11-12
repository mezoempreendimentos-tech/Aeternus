import yaml
import os
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÃO VISUAL
# ==============================================================================
class Cor:
    OK = '\033[92m' # Verde
    WARN = '\033[93m' # Amarelo
    FAIL = '\033[91m' # Vermelho
    RESET = '\033[0m'
    BOLD = '\033[1m'

def verificar_mundo():
    raiz_mundo = Path("data/world/zones")
    
    if not raiz_mundo.exists():
        print(f"{Cor.FAIL}❌ [ERRO CRÍTICO] O mundo não existe em '{raiz_mundo}'{Cor.RESET}")
        return

    print(f"{Cor.BOLD}🔍 O INQUISIDOR ACORDOU.{Cor.RESET}")
    print(f"   Escaneando os planos de existência em: {raiz_mundo}...\n")

    total_salas = 0
    total_mobs = 0
    total_items = 0
    total_zonas = 0
    zonas_com_erro = 0

    # Percorre AA (Área) -> RR (Região) -> ZZ (Zona)
    for area in sorted(raiz_mundo.iterdir()):
        if not area.is_dir() or area.name.startswith("."): continue
        
        for regiao in sorted(area.iterdir()):
            if not regiao.is_dir() or regiao.name.startswith("."): continue
            
            for zona in sorted(regiao.iterdir()):
                if not zona.is_dir() or zona.name.startswith("."): continue
                
                # --- DENTRO DE UMA ZONA ---
                total_zonas += 1
                erros_nesta_zona = []
                stats = {"rooms": 0, "mobs": 0, "items": 0}

                # 1. Verificar Salas
                try:
                    f_rooms = zona / "rooms.yaml"
                    if f_rooms.exists():
                        with open(f_rooms, 'r', encoding='utf-8') as f:
                            dados = yaml.safe_load(f)
                            stats["rooms"] = len(dados) if dados else 0
                except Exception as e:
                    erros_nesta_zona.append(f"Rooms YAML corrompido: {e}")

                # 2. Verificar Mobs
                try:
                    f_mobs = zona / "mobs.yaml"
                    if f_mobs.exists():
                        with open(f_mobs, 'r', encoding='utf-8') as f:
                            dados = yaml.safe_load(f)
                            stats["mobs"] = len(dados) if dados else 0
                except Exception as e:
                    erros_nesta_zona.append(f"Mobs YAML corrompido: {e}")

                # 3. Verificar Itens
                try:
                    f_items = zona / "items.yaml"
                    if f_items.exists():
                        with open(f_items, 'r', encoding='utf-8') as f:
                            dados = yaml.safe_load(f)
                            stats["items"] = len(dados) if dados else 0
                except Exception as e:
                    erros_nesta_zona.append(f"Items YAML corrompido: {e}")

                # --- RELATÓRIO DA ZONA ---
                nome_zona = zona.name
                if erros_nesta_zona:
                    zonas_com_erro += 1
                    print(f"{Cor.FAIL}💀 [FALHA] {nome_zona}{Cor.RESET}")
                    for erro in erros_nesta_zona:
                        print(f"   └─ {erro}")
                else:
                    # Só mostra se tiver conteúdo, para não poluir com zonas vazias
                    if sum(stats.values()) > 0:
                        print(f"{Cor.OK}✅ {nome_zona:<40}{Cor.RESET} | 🏠 {stats['rooms']:<4} 👹 {stats['mobs']:<4} ⚔️  {stats['items']:<4}")
                        total_salas += stats['rooms']
                        total_mobs += stats['mobs']
                        total_items += stats['items']

    print("\n" + "="*60)
    print(f"{Cor.BOLD}📊 RELATÓRIO FINAL DO CENSO AETERNUS{Cor.RESET}")
    print("="*60)
    print(f"🌍 Zonas Mapeadas:   {total_zonas}")
    print(f"🏠 Salas Reais:      {total_salas}")
    print(f"👹 Criaturas Vivas:  {total_mobs}")
    print(f"⚔️  Objetos Físicos:  {total_items}")
    print("-" * 60)
    
    if zonas_com_erro > 0:
        print(f"{Cor.FAIL}⚠️  ALERTA: {zonas_com_erro} zonas sofreram corrupção durante a transmutação.{Cor.RESET}")
    else:
        print(f"{Cor.OK}✨ SUCESSO ABSOLUTO: A integridade estrutural é de 100%.{Cor.RESET}")

if __name__ == "__main__":
    verificar_mundo()