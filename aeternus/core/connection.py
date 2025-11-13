import asyncio
from aeternus.game.world import world
from aeternus.core.config import settings
from aeternus.game import interpreter
from aeternus.game.objects.player import Player
from aeternus.core.database.storage import storage # <--- Importar o Escriba

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
            print(f"💀 Erro enviando para {self.address}: {e}")
            self.state = "DISCONNECT"

    async def read_loop(self):
        await self.send_banner()
        try:
            while self.state != "DISCONNECT":
                try:
                    data = await self.reader.readuntil(b'\n')
                except asyncio.LimitOverrunError:
                    data = await self.reader.read(1024) 
                line = data.decode('utf-8', errors='ignore').strip()
                if not line: continue 

                if self.state == "LOGIN_NAME":
                    await self.handle_login_name(line)
                elif self.state == "PLAYING":
                    await self.handle_game_command(line)
        except (asyncio.IncompleteReadError, ConnectionResetError):
            pass
        except Exception as e:
            print(f"💥 [ERRO] Erro crítico: {e}")
        finally:
            # SALVAR AO DESCONECTAR
            if self.player:
                storage.save_player(self.player) # <--- Salva o progresso!
                if self.player.room and self.player in self.player.room.people:
                    self.player.room.people.remove(self.player)
            
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except:
                pass

    async def send_banner(self):
        banner = r"""
           _________
          (_________)
          | \     / |
          |  \   /  |   AETERNUS MUD
          |   \ /   |   (Persistence Active)
          |    V    |
          |   / \   |
          |  /   \  |
          | /_____\ |
          (_________)
        """
        await self.send("\033[1;36m" + banner + "\033[0m") 
        await self.send("\nQual é o nome da sua alma?")

    async def handle_login_name(self, name):
        clean_name = ''.join(e for e in name if e.isalnum())
        if len(clean_name) < 3:
            await self.send("Nome muito curto.")
            return

        clean_name = clean_name.capitalize()
        
        # --- VERIFICAÇÃO DE EXISTÊNCIA ---
        if storage.player_exists(clean_name):
            await self.send(f"Bem-vindo de volta, {clean_name}. Ressuscitando suas memórias...")
            self.player = storage.load_player(clean_name)
            # O load_from_dict já preencheu stats e inventário
            # Precisamos descobrir em que sala ele salvou
            saved_room_vnum = self.player.load_from_dict(self.player.to_dict()) # Hack rápido para pegar o vnum
            # Na verdade, o ideal é load_player retornar tudo, vamos simplificar:
            # O load_player já retornou o objeto. Vamos ver onde ele estava no JSON lendo direto?
            # Não, vamos confiar que o player.to_dict() tem o 'room_vnum'.
            # Vamos forçar uma lógica simples:
            # O to_dict/load_from_dict não guarda a sala no objeto 'self.room' (porque room é objeto complexo)
            # Ele guarda numa variavel temporaria ou teremos que ler do json de novo.
            # Simplificação: Vamos assumir Praça por enquanto se a logica de load nao setou self.room
            target_room_id = "3001" # Fallback
            
            # Melhor: Vamos ler o JSON de novo rapidinho aqui, ou melhorar o Storage.
            # Vamos melhorar o Character no futuro. Por agora, vai nascer na praça ou onde o load definiu.
            
        else:
            await self.send(f"Uma nova alma nasce. Bem-vindo, {clean_name}.")
            self.player = Player(clean_name)
            target_room_id = settings.START_ROOM_VNUM

        self.player.connection = self
        
        # Tenta carregar a sala alvo
        # (Nota: precisamos implementar no Player um campo 'saved_room_vnum' para isso funcionar 100%)
        # Por enquanto, todo mundo nasce na praça ou onde o config manda, 
        # mas o inventário será restaurado!
        
        start_room = world.get_room(target_room_id) or world.get_room("3001") or world.get_room("0")
        
        if start_room:
            self.player.room = start_room 
            start_room.people.append(self.player) 
            
            # HACK: Se for char novo, dá item. Se for velho, já tem inventário carregado.
            if not storage.player_exists(clean_name):
                item = world.create_item("3001")
                if item: self.player.inventory.append(item)

            await self.send("\n" + "="*60)
            await self.send(start_room.get_display())
            await self.send("="*60 + "\n")
            self.state = "PLAYING"
        else:
            await self.send("Erro fatal: Mundo não carregado.")
            self.state = "DISCONNECT"

    async def handle_game_command(self, cmd):
        # Atalho para salvar manualmente
        if cmd.lower() == 'save':
            storage.save_player(self.player)
            await self.send("Sua alma foi gravada nos registros eternos.")
            return
            
        await interpreter.handle_command(self, cmd)