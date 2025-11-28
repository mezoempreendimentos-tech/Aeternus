# backend/game/commands/progression.py
from typing import List, Dict
from backend.models.character import Character
from backend.game.utils.vnum import VNum

# Definição hardcoded das classes para o protótipo.
# Futuramente isso deve ser lido de data/classes.json via Factory.
AVAILABLE_CLASSES = {
    "warrior": "Guerreiro (Mestre das Armas)",
    "mage": "Mago (Arcanista)",
    "rogue": "Ladino (Sombra)",
    "cleric": "Clérigo (Guardião)",
    "novice": "Novato (Recomeço Humilde)"
}

async def cmd_remort(ctx) -> str:
    """
    O CICLO DE SAMSARA (REMORT).
    
    Requisitos:
    1. Nível 100 (Mestria Máxima).
    2. Estar em um Altar de Criação (Flag de Sala: CREATION_ALTAR).
    
    Uso: renascer <nova_classe> <skill_para_herdar>
    """
    player: Character = ctx.player
    room = ctx.world.get_room(player.location_vnum)
    
    # 1. Validação de Local (O Altar)
    if not room:
        return "Você está perdido no vazio."
        
    # Descomente a linha abaixo quando tiver salas com a flag configurada nos JSONs
    # if not room.has_flag("CREATION_ALTAR"):
    #     return "Este local não possui a energia necessária para reescrever a alma. Busque um Altar de Criação."

    # 2. Validação de Nível (O Grande Filtro)
    # Nota: Para testes, você pode baixar esse requisito temporariamente
    if player.level < 100:
        return f"Sua alma ainda não atingiu a perfeição (Nível {player.level}/100). O ciclo exige plenitude."

    # 3. Interface de Ajuda / Sintaxe
    if not ctx.args or len(ctx.args) < 2:
        return (
            "== O RITUAL DE PASSAGEM ==\n"
            "Você atingiu o ápice desta forma. Para renascer, você deve escolher seu novo caminho "
            "e UMA técnica para levar consigo.\n\n"
            "Sintaxe: renascer <nova_classe> <skill_para_herdar>\n"
            "Exemplo: renascer mago aparar\n\n"
            f"Classes Disponíveis: {', '.join(AVAILABLE_CLASSES.keys())}\n"
            f"Suas Skills Atuais: {', '.join(player.skills) if player.skills else 'Nenhuma'}"
        )

    target_class_key = ctx.args[0].lower()
    skill_to_keep = ctx.args[1].lower()

    # 4. Validações de Escolha
    if target_class_key not in AVAILABLE_CLASSES:
        return f"Classe '{target_class_key}' desconhecida."
        
    if target_class_key == player.class_id:
        return "Você deve escolher uma forma diferente da atual para expandir sua alma."

    # Verifica se o jogador realmente tem a skill que quer manter
    if skill_to_keep not in player.skills and skill_to_keep not in player.inherited_skills:
        return f"Você não possui o conhecimento da skill '{skill_to_keep}' para levá-la."

    # 5. O SACRIFÍCIO (Execução)
    
    old_class = player.class_id
    
    # Adiciona a skill escolhida à lista de herança permanente
    if skill_to_keep not in player.inherited_skills:
        player.inherited_skills.append(skill_to_keep)
    
    # RESET TOTAL DE PROGRESSÃO
    player.class_id = target_class_key
    player.level = 1
    player.experience = 0
    player.remort_count += 1
    
    # Limpa skills ativas e restaura APENAS as herdadas
    # (Futuramente: adicionar skills iniciais da nova classe aqui)
    player.skills = player.inherited_skills.copy()
    
    # Registra no Diário Vital (Stats Pessoais)
    player.log_event(
        "REMORT_COMPLETE", 
        f"Atingiu a perfeição como {old_class.capitalize()} e renasceu como {target_class_key.capitalize()}, preservando {skill_to_keep}.", 
        10
    )
    
    # NOVO: Registra Remort no Grimório (Memória do Mundo)
    if hasattr(ctx.world, 'grimoire') and ctx.world.grimoire:
        # Pega o nome da sala de forma segura
        loc_name = "Desconhecido"
        current_room = ctx.world.get_room(player.location_vnum)
        if current_room:
            loc_name = current_room.title

        await ctx.world.grimoire.witness_event("remort", {
            "player_name": player.name,
            "player_level": 100,  # O nível que ele tinha antes do reset
            "old_class": old_class,
            "new_class": target_class_key,
            "remort_count": player.remort_count,
            "skill_kept": skill_to_keep,
            "location_vnum": player.location_vnum,
            "location_name": loc_name,
            "year": 1000 # Pegar do TimeEngine se disponível no futuro
        })
    
    # Mensagem de Retorno
    return (
        f"A dor é excruciante enquanto sua antiga forma de {old_class} se desfaz em luz...\n"
        f"--------------------------------------------------\n"
        f"Quando a poeira baixa, você se levanta novamente.\n"
        f"Você agora é um {AVAILABLE_CLASSES[target_class_key]} Nível 1.\n"
        f"A técnica '{skill_to_keep}' está gravada em sua alma para sempre."
    )