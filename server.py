import socket
import threading
import ssl 
from datetime import datetime

HOST = '' # Indica que o servidor escutará conexões em todas as interfaces de rede disponíveis.
PORT = 5000 # Porta TCP utilizada
SENHA_SALA = "1234"

clientes = [] # Lista de sockets SSL ativos de clientes conectados.
nomes = [] # Lista de nomes (strings) já escolhidos pelos usuários para evitar duplicidade.
HISTORICO_ARQUIVO = "chat_historico.txt"

# Cria um socket TCP padrão e relaciona à porta 5000
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORT))
servidor.listen()

# Cria um contexto SSL do tipo ssl.Purpose.CLIENT_AUTH e carrega o par de arquivos cert.pem e key.pem gerados anteriormente
contexto_ssl = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
contexto_ssl.load_cert_chain(certfile="cert.pem", keyfile="key.pem")  # Use seus arquivos
servidor_ssl = contexto_ssl.wrap_socket(servidor, server_side=True)  # Envolve o socket comum em um “socket SSL/TLS”. Isso faz com que, internamente, todos os accept() e recv() ocorram sobre um canal criptografado.

print(f"Servidor SSL escutando na porta {PORT}...")

# Cada mensagem transmitida (broadcast) é registrada, com o horário
def salvar_historico(msg):
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    with open(HISTORICO_ARQUIVO, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}{msg}\n")

# Itera sobre todos os sockets armazenados em clientes e envia (codificado em UTF-8) a mensagem para cada um
def broadcast(mensagem):
    salvar_historico(mensagem)
    for cliente in clientes:
        try:
            cliente.send(mensagem.encode())
        except:
            pass

# Cada nova conexão aceita pelo servidor é tratada em uma thread separada chamando essa função
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
    # Adiciona o nome à lista nomes e o socket à lista clientes.
    nomes.append(nome)
    clientes.append(cliente)
    print(f"{nome} entrou no chat.")
    broadcast(f"🔔 {nome} entrou no chat.")
    cliente.send(f"👥 Usuários online: {', '.join(nomes)}".encode())

    while True:
        try:
            msg = cliente.recv(1024).decode()
            # Se o cliente enviar a mensagem "sair" (case-insensitive), remove o socket de clientes, remove o nome correspondente de nomes
            if msg.lower() == 'sair':
                index = clientes.index(cliente)
                clientes.remove(cliente)
                cliente.close()
                nome_removido = nomes.pop(index)
                broadcast(f"🚪 {nome_removido} saiu do chat.")
                break
            # Se o cliente enviar "/usuarios", responde apenas a ele com a lista atual de nomes online
            elif msg.lower() == '/usuarios':
                resposta = "👥 Usuários online: " + ", ".join(nomes)
                cliente.send(resposta.encode())
            # Qualquer outra mensagem é repassada a todos via broadcast
            else:
                broadcast(f"{nome}: {msg}")
        except:
            break

while True:
    # O servidor fica em “escuta” (modo listen) aguardando novas conexões SSL
    #  imprime no console o endereço de quem conectou e cria uma nova thread que executa lidar_com_cliente(cliente)
    cliente, endereco = servidor_ssl.accept()  
    print(f"Nova conexão segura de {endereco}")
    thread = threading.Thread(target=lidar_com_cliente, args=(cliente,))
    thread.start()