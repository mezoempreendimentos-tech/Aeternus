from .entity import Entity
import asyncio
# REMOVIDO DAQUI: from aeternus.game.world import world

class Character(Entity):
    def __init__(self, vnum: str, name: str):
        super().__init__(vnum, name)
        
        self.max_hp = 100; self.hp = 100
        self.max_mana = 100; self.mana = 100
        self.max_stamina = 100; self.stamina = 100
        self.level = 1
        
        self.class_vnum = "class_novice"
        self.strength = 10; self.dexterity = 10; self.constitution = 10
        self.intelligence = 10; self.wisdom = 10; self.charisma = 10
        
        # --- Estado ---
        self.fighting = None 
        self.position = "standing"
        
        # --- Magia & Tempo ---
        self.spells_known = set()
        
        # Estrutura de Cast: { 'spell': SpellObj, 'target': CharObj, 'timer': int }
        self.casting = None 
        
        # Cooldowns: { 'spell_id': int_ticks_remaining }
        self.cooldowns = {} 
        
        self.inventory = []      
        self.equipment = {}      
        self.room = None         

    def get_short_desc(self): return self.name

    def get_display(self):
        status = ""
        if self.fighting: status = " \033[1;31m[LUTANDO]\033[0m"
        elif self.casting: status = " \033[1;36m(Conjurando...)\033[0m" # <--- Feedback visual
        elif self.position == "sleeping": status = " \033[1;34m(Dormindo)\033[0m"
        elif self.position == "resting": status = " \033[1;32m(Descansando)\033[0m"
        elif self.position == "meditating": status = " \033[1;35m(Meditando)\033[0m"
        return f"{self.name} está aqui.{status}"

    def is_alive(self): return self.hp > 0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0: self.hp = 0
        
        # Interrupção de Sono
        if self.position in ["sleeping", "meditating"]:
            self.position = "standing"
            self._send_async("\033[1;31mVOCÊ ACORDOU COM DOR!\033[0m")
            
        # Interrupção de Magia (Concentração)
        if self.casting:
            # Chance de falhar? Por enquanto falha sempre (Hardcore)
            self.casting = None
            self._send_async("\033[1;35mA dor quebra sua concentração! O feitiço se dissipa.\033[0m")

    def _send_async(self, msg):
        if hasattr(self, 'connection') and self.connection:
            asyncio.create_task(self.connection.send(msg))

    def regenerate(self):
        # --- IMPORTAÇÃO TARDIA ---
        from aeternus.game.world import world 
        
        if self.fighting: return 

        base_hp = self.max_hp * 0.05
        base_mn = self.max_mana * 0.05
        base_mv = self.max_stamina * 0.05
        
        season = world.current_season['name']
        if season == "Primoris": base_hp *= 1.10
        elif season == "Hiems": base_mv *= 0.90
        elif season == "Caducus": base_mn *= 1.05

        mult_hp = 1.0; mult_mn = 1.0; mult_mv = 1.0
        bonus_factor = 1.0 if world.is_night() else 0.5 
        penalty = 0.2 
        
        if self.position == "resting":
            mult_hp += bonus_factor; mult_mn -= penalty; mult_mv -= penalty
        elif self.position == "meditating":
            mult_mn += bonus_factor; mult_hp -= penalty; mult_mv -= penalty
        elif self.position == "sleeping":
            mult_mv += bonus_factor; mult_hp -= penalty; mult_mn -= penalty

        self.hp = min(self.max_hp, int(self.hp + (base_hp * mult_hp)))
        self.mana = min(self.max_mana, int(self.mana + (base_mn * mult_mn)))
        self.stamina = min(self.max_stamina, int(self.stamina + (base_mv * mult_mv)))