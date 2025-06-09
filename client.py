import socket
import threading
import tkinter as tk # Interface gráfica em Tkinter
from tkinter import scrolledtext, messagebox, simpledialog
import ssl  # Importação necessária para SSL

HOST = 'localhost'
PORT = 5000

class ClienteChat:
    def __init__(self):
        self.nome = ""
        
        # Configuração do contexto SSL
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = False  # Ignora verificação de hostname (para testes)
        context.verify_mode = ssl.CERT_NONE  # Ignora validação do certificado

        try:
            # Cria socket padrão e envolve em SSL
            self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cliente_ssl = context.wrap_socket(
                self.cliente, 
                server_hostname=HOST  # Necessário mesmo com check_hostname=False
            )
            self.cliente_ssl.connect((HOST, PORT))  # Conexão segura
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível conectar ao servidor.\nErro: {str(e)}")
            exit()

        # Autenticação de senha
        if not self.verificar_senha():
            messagebox.showerror("Erro", "Senha incorreta. Encerrando.")
            self.cliente_ssl.close()
            return

        self.iniciar_interface()
        self.verificar_nome()

        # Cria uma thread em background (self.receber_thread) para tratar mensagens recebidas do servidor (método receber).
        self.receber_thread = threading.Thread(target=self.receber)
        self.receber_thread.daemon = True
        self.receber_thread.start()
        # Iniciando o loop de eventos do Tkinter
        self.janela.mainloop()

    def verificar_senha(self):
        resposta = self.cliente_ssl.recv(1024).decode()  # Usa o socket SSL
        if resposta == "SENHA":
            senha = simpledialog.askstring("Senha da Sala", "Digite a senha para entrar:")
            self.cliente_ssl.send(senha.encode())  # Usa o socket SSL
            resultado = self.cliente_ssl.recv(1024).decode()  # Usa o socket SSL
            return resultado == "SENHA_OK"
        return False
    

    def iniciar_interface(self):
        self.janela = tk.Tk()
        self.janela.title("Chat em Grupo (Seguro)")

        self.txt_area = scrolledtext.ScrolledText(self.janela, wrap=tk.WORD, state='disabled') # Exibir mensagens
        self.txt_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.entrada_msg = tk.Entry(self.janela) # Digitar mensagens
        self.entrada_msg.pack(padx=10, pady=(0, 5), fill=tk.X)
        self.entrada_msg.bind("<Return>", lambda event: self.enviar_mensagem())

        self.frame_botoes = tk.Frame(self.janela)
        self.frame_botoes.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.btn_enviar = tk.Button(self.frame_botoes, text="Enviar", command=self.enviar_mensagem)
        self.btn_enviar.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.btn_sair = tk.Button(self.frame_botoes, text="Sair", command=self.sair)
        self.btn_sair.pack(side=tk.RIGHT, expand=True, fill=tk.X)

    def verificar_nome(self):
        while True:
            msg = self.cliente_ssl.recv(1024).decode()  # Usa o socket SSL
            if msg == "Digite seu nome: ":
                nome = self.solicitar_nome()
                self.cliente_ssl.send(nome.encode())  # Usa o socket SSL
                self.nome = nome
            elif msg == "NOME_REPETIDO":
                messagebox.showwarning("Nome em uso", "Esse nome já está em uso. Tente outro.")
            elif msg == "OK":
                self.adicionar_mensagem(f"✅ Você entrou como '{self.nome}'\n")
                break

    def solicitar_nome(self):
        nome = ""
        while not nome:
            nome = simpledialog.askstring("Nome", "Digite seu nome:")
            if not nome:
                messagebox.showwarning("Campo obrigatório", "Você precisa digitar um nome.")
        return nome

    # Executado em thread separada. 
    # Em loop infinito, faz self.cliente_ssl.recv(1024).decode() para obter mensagens do servidor
    def receber(self):
        while True:
            try:
                msg = self.cliente_ssl.recv(1024).decode()  # Usa o socket SSL
                self.adicionar_mensagem(msg + "\n")
            except:
                break

    def enviar_mensagem(self):
        msg = self.entrada_msg.get() #Obtem texto digitado
        if msg:
            self.cliente_ssl.send(msg.encode())  # Se nao vazio, envia mensagem 
            if msg.lower() == 'sair':
                self.sair()
            self.entrada_msg.delete(0, tk.END) # Limpa o campo de texto

    # area de texto como editavel
    def adicionar_mensagem(self, mensagem):
        self.txt_area.config(state='normal')
        self.txt_area.insert(tk.END, mensagem)
        self.txt_area.yview(tk.END)
        self.txt_area.config(state='disabled')

    def sair(self):
        try:
            self.cliente_ssl.send("sair".encode())  # Usa o socket SSL
        except:
            pass
        self.cliente_ssl.close()
        self.janela.destroy()

if __name__ == "__main__":
    ClienteChat()