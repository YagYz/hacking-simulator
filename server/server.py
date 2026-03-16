import socket
import threading
import time
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align

logs = ["[*] Sistem başlatıldı...", "[*] Ağ dinleniyor, bağlantı bekleniyor..."]
stats = {"bakiye": 0, "level": 1, "cpu_load": "12%"}

def socket_dinleyici():
    """Arka planda çalışıp client'tan gelen komutları yakalayan fonksiyon"""
    host = '127.0.0.1'
    port = 5555
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    
    conn, addr = server_socket.accept()
    logs.append(f"[bold green][+] Bağlantı sağlandı:[/bold green] {addr}")
    
    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            
            logs.append(f"[bold cyan]root@kali:~#[/bold cyan] {data}")
            
            if data == "hack localhost":
                logs.append("[bold yellow][!] Sızma başarılı! Hesaba +500$ eklendi.[/bold yellow]")
                stats["bakiye"] += 500
            elif data == "clear":
                logs.clear()
                
            if len(logs) > 15:
                logs.pop(0)
                
        except Exception as e:
            logs.append(f"[bold red]Hata:[/bold red] {e}")
            break
            
    conn.close()

def ekrani_olustur():
    """Rich kütüphanesi ile ekran düzenini (Layout) oluşturur"""
    layout = Layout()
    
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main")
    )
    
    layout["main"].split_row(
        Layout(name="stats", ratio=1),
        Layout(name="logs", ratio=2)
    )
    
    # 1. Başlık Paneli
    layout["header"].update(Panel(Align.center("[bold red]YagYz PESKER - TERMINAL OS v1.0[/bold red]"), style="red"))
    
    # 2. İstatistik Paneli
    stats_text = f"\n[bold green]Bakiye:[/bold green] ${stats['bakiye']}\n"
    stats_text += f"[bold blue]Level:[/bold blue] {stats['level']}\n"
    stats_text += f"[bold yellow]CPU Yükü:[/bold yellow] {stats['cpu_load']}\n"
    stats_text += "\n[bold magenta]Aktif Görevler:[/bold magenta]\n[ ] Hedef IP'yi tarat\n[ ] Veritabanı şifresini kır"
    
    layout["stats"].update(Panel(stats_text, title="[ Karakter & Sistem Durumu ]", border_style="green"))
    
    # 3. Log Paneli
    log_text = "\n".join(logs)
    layout["logs"].update(Panel(log_text, title="[ Ağ Trafik Analizi ]", border_style="blue"))
    
    return layout

def baslat():
    t = threading.Thread(target=socket_dinleyici, daemon=True)
    t.start()

    try:
        with Live(ekrani_olustur(), refresh_per_second=4) as live:
            while True:
                time.sleep(0.25)
                live.update(ekrani_olustur())
    except KeyboardInterrupt:
        print("\n[!] YagYz Terminal OS güvenli bir şekilde kapatılıyor. Bağlantılar kesildi.")

if __name__ == '__main__':
    baslat()