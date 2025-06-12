# Distribuidos


## Usar o tcpdump (ou Wireshark) no Windows

No Windows, o `tcpdump` não está disponível nativamente. Usaremos o **Wireshark** (interface gráfica) para capturar pacotes.

### Passo a Passo

#### 1. Instale o Wireshark
Baixe em [https://www.wireshark.org](https://www.wireshark.org) e instale normalmente.

---

#### 2. Capture o Tráfego Local (Loopback)

O Windows **não permite capturar tráfego de loopback (`localhost`) diretamente**. Para isso, use a ferramenta **RawCap**:

- Baixe o RawCap (gratuito) [aqui](http://www.netresec.com/?page=RawCap).
- Execute no PowerShell (como administrador):

```powershell
.\RawCap.exe 127.0.0.1 loopback.pcap
```

- Pressione `Ctrl+C` para parar a captura.
- Abra o arquivo `loopback.pcap` no Wireshark.

---

#### 3. Filtre a Porta 5000

No Wireshark, digite o seguinte filtro para visualizar apenas o tráfego do chat:

```wireshark
tcp.port == 5000
```

Isso mostrará apenas os pacotes relacionados ao seu servidor de chat.
