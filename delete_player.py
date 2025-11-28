import sys
import os

# Configuração de Ambiente para encontrar os módulos
sys.path.append(os.getcwd())

from backend.db.base import SessionLocal
from backend.db.models import PlayerORM
from sqlalchemy import func

def delete_player():
    print("\n" + "!" * 50)
    print("       💀 RITUAL DE BANIMENTO (DELETAR JOGADOR) 💀")
    print("!" * 50 + "\n")
    
    # Conecta ao Sarcófago
    session = SessionLocal()
    
    try:
        # 1. Busca o Alvo
        target_name = input("Digite o NOME EXATO do jogador a ser banido: ").strip()
        
        if not target_name:
            print("Nenhum nome dito. O ritual foi cancelado.")
            return

        # Busca case-insensitive para garantir
        player = session.query(PlayerORM).filter(func.lower(PlayerORM.name) == target_name.lower()).first()
        
        if not player:
            print(f"\n[ERRO] A alma de '{target_name}' não foi encontrada neste plano.")
            return

        # 2. Confirmação Final
        print(f"\n⚠️  ALVO ENCONTRADO: {player.name} (Nível {player.level}, ID: {player.id})")
        confirm = input("Tem certeza que deseja apagar esta existência para sempre? (sim/nao): ").lower()
        
        if confirm == "sim":
            # 3. O Banimento
            session.delete(player)
            session.commit()
            print(f"\n[SUCESSO] {player.name} foi removido da história. Seu registro é pó.")
        else:
            print("\nPiedade foi demonstrada. O jogador vive.")

    except Exception as e:
        print(f"\n[FALHA] O ritual falhou: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    delete_player()