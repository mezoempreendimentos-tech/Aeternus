import asyncio
import logging
from aeternus.game.world import world

class Connection:
    """
    Representa um fio ligando a alma do jogador (Telnet) ao Aeternus.
    Gerencia o envio e recebimento de dados e o estado atual da conexão.
    """
    
    # ⚠️ ATENÇÃO: Este método deve estar indentado (dentro da classe)
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.address = writer.get_extra_info('peername')
        self.state = "LOGIN_NAME" # Estados: LOGIN_NAME, PLAYING, DISCONNECT
        self.name = ""
        self.room = None
        
        print(f"🔌 [REDE] Nova conexão de {self.address}")

    async def send(self, text):
        """Envia texto para o cliente (com a quebra de linha correta do Telnet)."""
        try:
            # Telnet precisa de \r\n para pular linha corretamente
            msg = text.replace("\n", "\r\n") + "\r\n"
            self.writer.write(msg.encode('utf-8'))
            await self.writer.drain()
        except Exception as e:
            print(f"💀 Erro enviando para {self.address}: {e}")
            self.state = "DISCONNECT"

    async def read_loop(self):
        """O ouvido atento do servidor. Mantém a conexão viva."""
        # 1. Envia o Banner de Boas Vindas
        await self.send_banner()
        
        try:
            while self.state != "DISCONNECT":
                # 2. Espera o jogador digitar algo e apertar ENTER
                try:
                    data = await self.reader.readuntil(b'\n')
                except asyncio.LimitOverrunError:
                    data = await self.reader.read(1024) 
                
                line = data.decode('utf-8', errors='ignore').strip()
                
                if not line: continue 

                # 3. Processa o comando baseado no estado atual
                if self.state == "LOGIN_NAME":
                    await self.handle_login_name(line)
                elif self.state == "PLAYING":
                    await self.handle_game_command(line)
                    
        except (asyncio.IncompleteReadError, ConnectionResetError):
            print(f"🔌 [REDE] {self.address} desconectou (Conexão fechada).")
        except Exception as e:
            print(f"💥 [ERRO] Erro crítico na conexão {self.address}: {e}")
        finally:
            # Garante que o jogador saia da sala se desconectar
            if self.room and self in self.room.people:
                self.room.people.remove(self)
            
            print(f"🔌 [REDE] Encerrando sessão de {self.address}")
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except:
                pass

    async def send_banner(self):
        """Envia a arte ASCII de abertura."""
        # Arte: A Ampulheta do Destino (Timeglass)
        banner = r"""
             __________
        ____/          \____
       /  ________________  \
       | | ______________ | |
       | | |            | | |
       | | |  .:....:.  | | |
       | | | .::::::::. | | |
       | | | :::::::::. | | |
       | | | '::::::::' | | |
       | | |   '::::'   | | |
       | | |    ':.     | | |
       | |  \    .     /  | |
       | |   \   .    /   | |
       | |    \  .   /    | |
       | |     \ .  /     | |
       | |      \  /      | |
       | |      (  )      | |
       | |      /  \      | |
       | |     / .. \     | |
       | |    / .... \    | |
       | |   / ...... \   | |
       | |  / :::::::: \  | |
       | | / :::::::::: \ | |
       | |/ :::::::::::: \| |
       | |::::::::::::::::| |
       | |________________| |
       \____________________/
    """
        await self.send("\033[1;36m" + banner + "\033[0m") 
        await self.send("\033[1;37m" + "      A E T E R N U S   M U D".center(60) + "\033[0m")
        await self.send("\033[1;33m" + "  \"O tempo devora tudo, menos a lenda.\"".center(60) + "\033[0m")
        await self.send("\n" + "Qual é o nome da sua alma?".center(60))

    async def handle_login_name(self, name):
        """Processa o nome digitado no login."""
        clean_name = ''.join(e for e in name if e.isalnum())
        
        if len(clean_name) < 3:
            await self.send("Um nome tão curto se perderá nas areias do tempo. Tente novamente.")
            return

        self.name = clean_name.capitalize()
        await self.send(f"\nSaudações, {self.name}. Preparando sua encarnação...")
        
        # --- A MATERIALIZAÇÃO (Usa o Atlas carregado) ---
        # Tenta pegar a Sala 3001 (Midgaard Temple Square) ou 3000 ou 0
        start_room = world.get_room("3001") or world.get_room("3000") or world.get_room("0")
        
        if start_room:
            self.room = start_room 
            start_room.people.append(self) # Adiciona o jogador na sala
            
            # Mostra a sala
            await self.send("\n" + "="*60)
            await self.send(start_room.get_display())
            await self.send("="*60 + "\n")
            
            self.state = "PLAYING"
        else:
            await self.send("💀 ERRO CRÍTICO: O mundo não existe (Nenhuma sala carregada).")
            await self.send("   Verifique se 'world.load_assets()' foi chamado no main.py.")
            self.state = "DISCONNECT"

    async def handle_game_command(self, cmd):
        """Processa comandos normais de jogo."""
        cmd = cmd.lower().strip()
        
        if cmd == 'quit':
            await self.send("O tempo parou para você.")
            self.state = "DISCONNECT"
            
        elif cmd == 'look' or cmd == 'l':
            if hasattr(self, 'room') and self.room:
                await self.send(self.room.get_display())
            else:
                await self.send("Você está perdido no éter.")
                
        else:
            await self.send(f"Você diz: '{cmd}'")