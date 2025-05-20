import socket

import threading

import tkinter as tk

from tkinter import scrolledtext, messagebox, simpledialog



HOST = 'localhost'

PORT = 5000



class ClienteChat:

    def __init__(self):

        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.nome = ""



        try:

            self.cliente.connect((HOST, PORT))

        except:

            messagebox.showerror("Erro", "Não foi possível conectar ao servidor.")

            exit()



        # Autenticação de senha

        if not self.verificar_senha():

            messagebox.showerror("Erro", "Senha incorreta. Encerrando.")

            self.cliente.close()

            return



        self.iniciar_interface()

        self.verificar_nome()



        self.receber_thread = threading.Thread(target=self.receber)

        self.receber_thread.daemon = True

        self.receber_thread.start()

        self.janela.mainloop()



    def verificar_senha(self):

        resposta = self.cliente.recv(1024).decode()

        if resposta == "SENHA":

            senha = simpledialog.askstring("Senha da Sala", "Digite a senha para entrar:")

            self.cliente.send(senha.encode())

            resultado = self.cliente.recv(1024).decode()

            return resultado == "SENHA_OK"

        return False



    def iniciar_interface(self):

        self.janela = tk.Tk()

        self.janela.title("Chat em Grupo")



        self.txt_area = scrolledtext.ScrolledText(self.janela, wrap=tk.WORD, state='disabled')

        self.txt_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)



        self.entrada_msg = tk.Entry(self.janela)

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

            msg = self.cliente.recv(1024).decode()

            if msg == "Digite seu nome: ":

                nome = self.solicitar_nome()

                self.cliente.send(nome.encode())

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



    def receber(self):

        while True:

            try:

                msg = self.cliente.recv(1024).decode()

                self.adicionar_mensagem(msg + "\n")

            except:

                break



    def enviar_mensagem(self):

        msg = self.entrada_msg.get()

        if msg:

            self.cliente.send(msg.encode())

            if msg.lower() == 'sair':

                self.sair()

            self.entrada_msg.delete(0, tk.END)



    def adicionar_mensagem(self, mensagem):

        self.txt_area.config(state='normal')

        self.txt_area.insert(tk.END, mensagem)

        self.txt_area.yview(tk.END)

        self.txt_area.config(state='disabled')



    def sair(self):

        try:

            self.cliente.send("sair".encode())

        except:

            pass

        self.cliente.close()

        self.janela.destroy()



if __name__ == "__main__":

    ClienteChat()
