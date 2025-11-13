import asyncio
from aeternus.game.world import world
from aeternus.core.config import settings
from aeternus.game import interpreter
from aeternus.game.objects.player import Player
from aeternus.core.database.storage import storage

class Connection:
    
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.address = writer.get_extra_info('peername')
        self.state = "LOGIN_NAME"
        self.name = ""
        self.player = None

    async def send(self, text):
        try:
            msg = text.replace("\n", "\r\n") + "\r\n"
            self.writer.write(msg.encode('utf-8'))
            await self.writer.drain()
        except Exception as e:
            # print(f"💀 Erro de socket: {e}")
            self.state = "DISCONNECT"

    async def read_loop(self):
        await self.send_banner()
        
        try:
            while self.state != "DISCONNECT":
                try:
                    data = await self.reader.readuntil(b'\n')
                except asyncio.LimitOverrunError:
                    data = await self.reader.read(1024) 
                except:
                    break # Conexão caiu
                
                line = data.decode('utf-8', errors='ignore').strip()
                if not line: continue 

                if self.state == "LOGIN_NAME":
                    await self.handle_login_name(line)
                elif self.state == "PLAYING":
                    await self.handle_game_command(line)
                    
        finally:
            # --- ROTINA DE DESCONEXÃO ---
            if self.player:
                print(f"🔌 [LOGOUT] Salvando {self.player.name}...")
                
                # 1. Salva no disco (incluindo sala atual)
                storage.save_player(self.player)
                
                # 2. Remove da lista global (WHO)
                world.remove_player(self.player)
                
                # 3. Remove da sala física
                if self.player.room and self.player in self.player.room.people:
                    self.player.room.people.remove(self.player)
            
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except: pass

    async def send_banner(self):
        banner = r"""
           _________
          (_________)
          | \     / |
          |  \   /  |   AETERNUS MUD
          |   \ /   |   (Alpha Build)
          |    V    |
          |   / \   |
          |  /   \  |
          | /_____\ |
          (_________)
        """
        await self.send("\033[1;36m" + banner + "\033[0m") 
        await self.send("\nQual é o nome da sua alma?")

    async def handle_login_name(self, name):
        clean_name = ''.join(e for e in name if e.isalnum()).capitalize()
        if len(clean_name) < 3:
            await self.send("Nome inválido.")
            return

        # 1. Carregar ou Criar
        if storage.player_exists(clean_name):
            await self.send(f"Bem-vindo de volta, {clean_name}.")
            self.player = storage.load_player(clean_name)
        else:
            await self.send(f"Bem-vindo, novo herói {clean_name}.")
            self.player = Player(clean_name)

        # 2. Vincular
        self.player.connection = self
        
        # 3. Registrar no Mundo (CRÍTICO PARA O WHO)
        world.add_player(self.player)

        # 4. Determinar Spawn (Lógica de Recuperação)
        target_vnum = None
        
        # A) Tenta a sala salva no JSON
        if self.player.saved_room_vnum:
            target_vnum = self.player.saved_room_vnum
            
            # Verifica se essa sala AINDA existe no mundo (pode ter sido deletada)
            if not world.get_room(target_vnum):
                await self.send(f"\033[1;31mAviso: Sua sala antiga ({target_vnum}) colapsou. Realocando...\033[0m")
                target_vnum = None # Força fallback

        # B) Fallback para a Sala Inicial do Config (.env)
        if not target_vnum:
            target_vnum = settings.START_ROOM_VNUM

        # C) Tenta carregar a sala final
        start_room = world.get_room(target_vnum)
        
        # D) Fallback Supremo (Limbo 0 ou Praça Antiga 3001) se o Config estiver errado
        if not start_room:
            print(f"⚠️ [ALERTA] Falha crítica de spawn em {target_vnum}. Tentando emergência...")
            start_room = world.get_room("0") or world.get_room("3001")

        # 5. Materializar
        if start_room:
            self.player.room = start_room 
            start_room.people.append(self.player)
            
            # Hack de item inicial para chars novos
            if not storage.player_exists(clean_name) and not self.player.inventory:
                 item = world.create_item("3001") or world.create_item("1")
                 if item: self.player.inventory.append(item)

            await self.send("\n" + "="*60)
            await self.send(start_room.get_display())
            self.state = "PLAYING"
        else:
            await self.send("Erro fatal: O universo não possui salas. Contate o Admin.")
            self.state = "DISCONNECT"

    async def handle_game_command(self, cmd):
        # Atalho rápido para salvar
        if cmd.lower() == 'save':
            storage.save_player(self.player)
            await self.send("Estado salvo.")
            return
        await interpreter.handle_command(self, cmd)