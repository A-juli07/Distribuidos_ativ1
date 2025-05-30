import socket
import threading
import ssl 
from datetime import datetime

HOST = ''
PORT = 5000
SENHA_SALA = "1234"

clientes = []
nomes = []
HISTORICO_ARQUIVO = "chat_historico.txt"

# Configuração do socket seguro
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORT))
servidor.listen()

# Criação do contexto SSL
contexto_ssl = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
contexto_ssl.load_cert_chain(certfile="cert.pem", keyfile="key.pem")  # Use seus arquivos
servidor_ssl = contexto_ssl.wrap_socket(servidor, server_side=True)  # Socket seguro

print(f"Servidor SSL escutando na porta {PORT}...")

def salvar_historico(msg):
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    with open(HISTORICO_ARQUIVO, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}{msg}\n")

def broadcast(mensagem):
    salvar_historico(mensagem)
    for cliente in clientes:
        try:
            cliente.send(mensagem.encode())
        except:
            pass

def lidar_com_cliente(cliente):
    # Autenticação da sala
    cliente.send("SENHA".encode())
    senha = cliente.recv(1024).decode()
    
    if senha != SENHA_SALA:
        cliente.send("SENHA_ERRADA".encode())
        cliente.close()
        return
    else:
        cliente.send("SENHA_OK".encode())

    # Solicitação de nome
    while True:
        cliente.send("Digite seu nome: ".encode())
        nome = cliente.recv(1024).decode().strip()
        if nome and nome not in nomes:
            cliente.send("OK".encode())
            break
        else:
            cliente.send("NOME_REPETIDO".encode())

    nomes.append(nome)
    clientes.append(cliente)
    print(f"{nome} entrou no chat.")
    broadcast(f"🔔 {nome} entrou no chat.")
    cliente.send(f"👥 Usuários online: {', '.join(nomes)}".encode())

    while True:
        try:
            msg = cliente.recv(1024).decode()
            if msg.lower() == 'sair':
                index = clientes.index(cliente)
                clientes.remove(cliente)
                cliente.close()
                nome_removido = nomes.pop(index)
                broadcast(f"🚪 {nome_removido} saiu do chat.")
                break
            elif msg.lower() == '/usuarios':
                resposta = "👥 Usuários online: " + ", ".join(nomes)
                cliente.send(resposta.encode())
            else:
                broadcast(f"{nome}: {msg}")
        except:
            break

while True:
    # Aceita conexões SSL
    cliente, endereco = servidor_ssl.accept()  
    print(f"Nova conexão segura de {endereco}")
    thread = threading.Thread(target=lidar_com_cliente, args=(cliente,))
    thread.start()