# backend/game/engines/combat/flavor.py
import random

class CombatNarrator:
    """
    Gera descrições viscerais para momentos extremos do combate.
    """

    # =========================================================================
    # FATALITIES (Sucesso Extremo - Top 2% do Roll)
    # =========================================================================
    FATALITIES = {
        "slash": [
            "{att} descreve um arco perfeito com sua lâmina, separando carne, tendão e orgulho de {defender} num único movimento fluido!",
            "O aço de {att} canta uma canção de morte, abrindo uma fonte arterial em {defender} que pinta o chão de carmesim!",
            "Com precisão cirúrgica, {att} encontra a falha na defesa e fatia {defender} com uma brutalidade que gela a espinha!",
            "A lâmina de {att} se torna um borrão prateado, desenhando linhas vermelhas profundas na anatomia de {defender}!",
        ],
        "blunt": [
            "O impacto da arma de {att} ressoa como um trovão, pulverizando os ossos de {defender} sob o peso de uma força incontrolável!",
            "{att} converte energia cinética em pura destruição, fazendo o corpo de {defender} dobrar em um ângulo antinatural!",
            "Houve um som úmido e crocante quando {att} conectou o golpe, transformando a anatomia de {defender} em uma pasta irreconhecível!",
            "Como um martelo divino, {att} esmaga {defender}, enviando ondas de choque através de seu esqueleto!",
        ],
        "pierce": [
            "{att} estoca com velocidade de víbora, enterrando a arma profundamente em {defender} até encontrar o outro lado!",
            "Como uma agulha atravessando tecido, {att} perfura {defender}, atingindo órgãos vitais com uma precisão aterrorizante!",
            "{att} ignora a armadura de {defender} completamente, cravando a ponta de sua arma onde a vida é mais frágil!",
            "Um movimento rápido, um brilho metálico, e {att} retira sua arma coberta pelo sangue profundo de {defender}!",
        ],
        "magic": [
            "O ar crepita e o cheiro de ozônio preenche a sala enquanto {att} desintegra a matéria de {defender} com poder arcano puro!",
            "{att} canaliza o caos primordial, envolvendo {defender} em uma tempestade de energia que rasga a própria realidade!",
            "Chamas etéreas consomem {defender} enquanto {att} pronuncia a palavra final de poder!",
        ],
        "default": [
            "{att} desfere um golpe de mestre, humilhando {defender} com uma exibição de poder avassalador!",
            "Com um rugido primal, {att} sobrepuja completamente a defesa de {defender}!",
        ]
    }

    # =========================================================================
    # FUMBLES (Falha Crítica - Pior 2% do Roll)
    # =========================================================================
    FUMBLES = [
        "{att} tropeça nos próprios pés num momento de incompetência suprema, expondo-se completamente!",
        "A arma de {att} escapa de seus dedos suados, voando de forma cômica e inútil!",
        "{att} calcula mal a distância e golpeia violentamente o ar, quase deslocando o ombro na vergonha!",
        "Numa exibição patética, {att} perde o equilíbrio e quase cai de cara no chão antes de completar o ataque.",
        "{att} hesita no último segundo, transformando um ataque promissor em um movimento desajeitado.",
    ]

    @staticmethod
    def get_fatality(attacker_name, defender_name, dmg_type):
        """Retorna uma descrição de Fatality formatada."""
        # Tenta pegar específico do tipo, senão vai pro default
        key = dmg_type if dmg_type in CombatNarrator.FATALITIES else "default"
        templates = CombatNarrator.FATALITIES[key]
        
        template = random.choice(templates)
        # CORREÇÃO: Usando 'defender' como chave para evitar conflito com keyword 'def'
        return template.format(att=attacker_name, defender=defender_name)

    @staticmethod
    def get_fumble(attacker_name):
        """Retorna uma descrição de Falha Crítica."""
        template = random.choice(CombatNarrator.FUMBLES)
        return template.format(att=attacker_name)