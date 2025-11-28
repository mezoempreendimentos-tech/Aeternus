import asyncio
import logging
import sys
import os

# Configura path
sys.path.append(os.getcwd())

from backend.game.world.world_manager import WorldManager
from backend.game.engines.lore.grimoire import NPCMemory

# Logger
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("SimulacaoLore")

async def run_simulation():
    print("\n📜 --- INICIANDO SIMULAÇÃO: O TESTE DO BARDO --- 📜\n")
    
    # 1. Inicializa o Mundo
    world = WorldManager()
    await world.start_up()
    
    if not world.grimoire:
        print("Erro: Grimório offline.")
        return

    # 2. INVOCANDO O POETA (Manual)
    bardo = world.spawn_npc(100001, 100001) 
    if bardo:
        bardo.name = "Dandelion, o Bardo"
        bardo.description = "Um poeta famoso com um alaúde barulhento."
        bardo.uid = "npc_bardo_teste"
        room = world.get_room(100001)
        if room:
            room.npcs_here.append(bardo.uid)
            
        # Dando Cérebro ao Bardo (Skill 100)
        world.grimoire.npc_memories[bardo.uid] = NPCMemory(
            npc_uid=bardo.uid,
            storytelling_skill=100, 
            known_legends=[]
        )
        print(f"✨ NPC CRIADO: {bardo.name} (Skill de História: 100/100)")
    else:
        print("Erro ao spawnar o bardo.")
        return

    # 3. O Evento Épico
    print("\n⚔️  EVENTO: Galahad mata o Dragão Vermelho!")
    event_data = {
        "player_name": "Galahad",
        "player_level": 50,
        "enemy_name": "Ignis, o Dragão",
        "enemy_level": 60,
        "damage": 5000,
        "location_vnum": 100001,
        "location_name": "A Montanha da Perdição",
        "zone_id": 1,
        "weapon_type": "sword",
        "year": 1000
    }

    # Grimório testemunha
    await world.grimoire.witness_event("fatality", event_data)
    
    # 4. Recupera a Lenda
    legends = world.grimoire.get_legends_about_player("Galahad")
    if not legends:
        print("A lenda não foi criada.")
        return
    lenda = legends[0]

    # 5. O Bardo Aprende
    memoria_bardo = world.grimoire.npc_memories[bardo.uid]
    memoria_bardo.known_legends.append(lenda.id)
    lenda.believers.append(bardo.uid)
    
    # 6. O Bardo Conta
    print(f"\n🎤 OUVINDO {bardo.name.upper()}:")
    
    # CORREÇÃO AQUI: A variável agora é consistente ('narrativa')
    narrativa = await world.grimoire.npc_tell_legend(bardo.uid, lenda.id)
    
    print("-" * 60)
    print(narrativa)
    print("-" * 60)
    
    # Mostra qual versão foi escolhida
    if len(lenda.versions) > 1:
        # Verifica se a versão poética (índice -1) está contida no texto narrado
        if lenda.versions[-1] in narrativa:
            print("\n✅ SUCESSO: O Bardo usou a versão POÉTICA (IA)!")
        else:
            print("\n❌ FALHA: O Bardo usou a versão Factual (Seca).")
    else:
        print("\n⚠️ AVISO: A lenda só tem 1 versão (Factual). A IA falhou ou estava desligada.")

    print("\n📜 --- FIM DA SIMULAÇÃO ---")

if __name__ == "__main__":
    asyncio.run(run_simulation())