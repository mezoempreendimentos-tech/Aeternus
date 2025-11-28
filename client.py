import sys
import os
import httpx
import time

SERVER_URL = "http://localhost:8000/api"

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("=" * 60)
    print("        ⚔️  AETERNUS MUD - CLIENTE DE ACESSO v0.2 ⚔️")
    print("=" * 60)

def api_post(endpoint, data):
    try:
        response = httpx.post(f"{SERVER_URL}/{endpoint}", json=data, timeout=10.0)
        if response.status_code >= 400:
            print(f"\n[ERRO] {response.text}")
            return None
        return response.json()
    except Exception as e:
        print(f"\n[FALHA] Servidor offline ou erro: {e}")
        return None

def login_flow():
    print("\n1. Entrar (Login)")
    print("2. Criar Nova Lenda (Registro)")
    print("3. Sair")
    
    choice = input("\nEscolha: ").strip()
    
    if choice == "1":
        username = input("Usuario: ").strip()
        password = input("Senha: ").strip()
        payload = {"username": username, "password": password}
        response = api_post("auth/login", payload)
        if response: return response["player_id"], response["message"]
            
    elif choice == "2":
        print("\n--- CRIAÇÃO DE PERSONAGEM ---")
        username = input("Nome do Herói: ").strip()
        password = input("Senha: ").strip()
        print("\nRaças: humano, elfo, anao")
        race = input("Raça: ").strip().lower() or "humano"
        
        # REMOVIDO: Seleção de classe. O backend define como Novice.
        
        payload = {
            "username": username, 
            "password": password,
            "race": race
        }
        response = api_post("auth/register", payload)
        if response: return response["player_id"], response["message"]
            
    elif choice == "3":
        sys.exit(0)
        
    return None, None

def game_loop(player_id):
    print("\n" + "-" * 60)
    print("Conectado! Comandos: olhar, inventario, pegar <item>, largar <item>, sair")
    print("-" * 60 + "\n")

    api_post("command", {"player_id": player_id, "command": "olhar"})

    while True:
        try:
            cmd = input("\n> ").strip()
            if not cmd: continue
            if cmd.lower() in ["sair", "quit"]: break
            
            data = api_post("command", {"player_id": player_id, "command": cmd})
            if data and "response" in data:
                print(f"\n{data['response']}")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()