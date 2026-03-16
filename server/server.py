import socket
import threading
import time
import os
import json
from pathlib import Path
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align

# Modern ve Güvenli Yol Tanımlamaları
BASE_DIR = Path(__file__).resolve().parent.parent
JSON_YOLU = BASE_DIR / 'data' / 'missions.json'
SAVE_YOLU = BASE_DIR / 'data' / 'savegame.json'

def json_oku():
    try:
        with open(JSON_YOLU, 'r', encoding='utf-8') as f:
            return json.load(f)["gorevler"]
    except FileNotFoundError:
        return []

hedefler = json_oku()
logs = ["[*] YagYz C2 Ana Sistemi başlatıldı...", "[*] Şifreli ağ dinleniyor, ajanlardan bağlantı bekleniyor..."]

# --- SAVE / LOAD SİSTEMİ ---
def oyunu_yukle():
    if SAVE_YOLU.exists():
        try:
            with open(SAVE_YOLU, 'r', encoding='utf-8') as f:
                kayit = json.load(f)
                logs.append("[bold green][+] YagYz Ajan Profili diskten başarıyla yüklendi.[/bold green]")
                return kayit.get("stats", {"bakiye": 0, "level": 1, "xp": 0, "cpu_load": "12%"}), kayit.get("tamamlanan_gorevler", [])
        except: pass
    logs.append("[bold yellow][*] Yeni profil oluşturuldu. Kayıt dosyası bulunamadı.[/bold yellow]")
    return {"bakiye": 0, "level": 1, "xp": 0, "cpu_load": "12%"}, []

stats, tamamlanan_gorevler = oyunu_yukle()

if "donanim" not in stats:
    stats["donanim"] = {"cpu": "Standart", "ram": "8GB", "kits": []}
    
if "envanter" not in stats:
    stats["envanter"] = {"cpu": 0, "gpu": 0, "ram": 0, "kits": []}

def oyunu_kaydet():
    kayit = {"stats": stats, "tamamlanan_gorevler": tamamlanan_gorevler}
    with open(SAVE_YOLU, 'w', encoding='utf-8') as f:
        json.dump(kayit, f, indent=4)
# ---------------------------------

def ekrani_temizle():
    os.system('clear')

def gorev_tamamla(hedef_ip, eylem, ekstra_bilgi=None):
    hedef_data = next((h for h in hedefler if h.get("hedef_ip") == hedef_ip), None)
    if not hedef_data: return
    
    gorev_id = hedef_data["id"]
    if gorev_id in tamamlanan_gorevler: return 
        
    if stats["level"] < hedef_data.get("min_level", 1): return
        
    istenen_eylem = hedef_data.get("istenen_eylem")
    istenen_dosya = hedef_data.get("istenen_dosya")
    
    basarili = False
    if eylem == "TARAMA_YAPILDI" and istenen_eylem == "tarama_yapildi": basarili = True
    elif eylem == "SIZMA_BASARILI" and istenen_eylem == "sizma_basarili": basarili = True
    elif eylem == "DOSYA_INDIRILDI" and istenen_eylem == "dosya_indirildi":
        if ekstra_bilgi == istenen_dosya: basarili = True
            
    if basarili:
        stats["bakiye"] += hedef_data["odul"]
        stats["xp"] += hedef_data["xp"]
        tamamlanan_gorevler.append(gorev_id)
        logs.append(f"[bold green][+] GÖREV BAŞARILI ({gorev_id}): Kripto cüzdana ${hedef_data['odul']} aktarıldı![/bold green]")
        
        if stats["xp"] >= 100:
            stats["level"] += 1
            stats["xp"] = 0 
            logs.append(f"[bold magenta][!] LEVEL UP! Artık Seviye {stats['level']} oldun. DarkNet'te yeni işler açıldı.[/bold magenta]")
            
        oyunu_kaydet()

def socket_dinleyici():
    host = '127.0.0.1'
    port = 5555
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    
    conn, addr = server_socket.accept()
    logs.append(f"[bold green][+] Şifreli Tünel Açıldı. Ajan Bağlandı:[/bold green] {addr}")
    
    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data: break
            
            if not any(data.startswith(s) for s in ["SIZMA", "TARAMA", "FIREWALL", "DOSYA"]):
                logs.append(f"[bold cyan]root@yagyz:~#[/bold cyan] {data}")
            
            # --- YENİ TEMAYA UYGUN LOG GÜNCELLEMELERİ ---
            if data.startswith("TARAMA_YAPILDI"):
                hedef_ip = data.split()[1]
                logs.append(f"[bold yellow][*] İSTİHBARAT: {hedef_ip} ağ haritası ve port analizi tamamlandı.[/bold yellow]")
                gorev_tamamla(hedef_ip, "TARAMA_YAPILDI")
                
            elif data.startswith("FIREWALL_BYPASS"):
                parcalar = data.split()
                hedef_ip, hedef_port = parcalar[1], parcalar[2]
                logs.append(f"[bold magenta][!] WAF ÇÖKÜŞÜ: {hedef_ip}:{hedef_port} üzerindeki güvenlik duvarı aşıldı![/bold magenta]")

            elif data.startswith("SIZMA_BASARILI"):
                hedef_ip = data.split()[1]
                # Log mesajı "Crack" yerine "Exploit/Zafiyet" temasına uygun hale getirildi
                logs.append(f"[bold yellow][*] EXPLOIT BAŞARILI: {hedef_ip} sistemindeki zafiyet sömürüldü, root erişimi sağlandı.[/bold yellow]")
                gorev_tamamla(hedef_ip, "SIZMA_BASARILI")
                
            elif data.startswith("DOSYA_INDIRILDI"):
                parcalar = data.split()
                hedef_ip, dosya_adi = parcalar[1], parcalar[2]
                logs.append(f"[bold cyan][+] VERİ SIZINTISI: {hedef_ip} sunucusundan '{dosya_adi}' başarıyla çekildi.[/bold cyan]")
                gorev_tamamla(hedef_ip, "DOSYA_INDIRILDI", ekstra_bilgi=dosya_adi)
                
            elif data.startswith("SATIN_ALMA"):
                parcalar = data.split()
                fiyat = int(parcalar[1])
                urun_tipi = parcalar[2] # donanim / kit
                urun_id = parcalar[3]   # H-CPU-1 gibi
                urun_ismi = " ".join(parcalar[4:])
                
                if stats["bakiye"] >= fiyat:
                    if urun_tipi == "donanim":
                        # Parça tipini ve tier'ı ID'den veya JSON'dan çekebiliriz
                        # Basitlik için ID kontrolü:
                        p_tip = "cpu" if "CPU" in urun_id else "gpu" if "GPU" in urun_id else "ram"
                        t_seviye = int(urun_id.split('-')[-1]) # Sondaki rakamı al
                        
                        # Eğer zaten bu tier veya üstüne sahipse engelle
                        if stats["envanter"].get(p_tip, 0) >= t_seviye:
                            conn.send("ZATEN_SAHIP".encode('utf-8'))
                            continue
                        
                        stats["envanter"][p_tip] = t_seviye
                        stats["donanim"][p_tip] = urun_ismi # Stats ekranı için isim
                    else:
                        # Kitler sınırsız alınabilir
                        if urun_ismi not in stats["donanim"]["kits"]:
                            stats["donanim"]["kits"].append(urun_ismi)
                    
                    stats["bakiye"] -= fiyat
                    logs.append(f"[bold green][+] DONANIM GÜNCELLENDİ:[/bold green] {urun_ismi}")
                    oyunu_kaydet()
                    conn.send("ONAY".encode('utf-8'))
                else:
                    conn.send("YETERSIZ_BAKIYE".encode('utf-8'))

            elif data == "clear":
                logs.clear()
                
            if len(logs) > 15:
                logs.pop(0)
                
        except Exception as e:
            logs.append(f"[bold red]Bağlantı koptu:[/bold red] {e}")
            break
    conn.close()

def ekrani_olustur():
    layout = Layout()
    layout.split_column(Layout(name="header", size=3), Layout(name="main"))
    layout["main"].split_row(Layout(name="stats", ratio=1), Layout(name="logs", ratio=2))
    
    layout["header"].update(Panel(Align.center("[bold red]YAGYZ C2 SERVER - COMMAND & CONTROL[/bold red]"), style="red"))
    
    # --- KAYMAYI ÖNLEYEN YENİ STATS TASARIMI ---
    s_donanim = stats.get("donanim", {"cpu": "Standart", "ram": "8GB", "kits": []})
    e = stats.get("envanter", {"cpu": 0, "gpu": 0, "ram": 0})
    
    # Rich stili kullanarak metni oluşturuyoruz (ANSI kodları \033... yerine [renk]...)
    stats_text = f"\n[bold green]Kripto Bakiye:[/bold green] ${stats['bakiye']}\n"
    stats_text += f"[bold blue]Hacker Level:[/bold blue] {stats['level']} (XP: {stats['xp']}/100)\n"
    stats_text += f"[bold yellow]CPU Yükü:[/bold yellow] {stats['cpu_load']}\n"
    
    stats_text += "\n[bold cyan]SİSTEM BİLEŞENLERİ:[/bold cyan]\n"
    stats_text += f" [white]CPU:[/white] {s_donanim['cpu']} [green](x{1 + e['cpu']*0.5})[/green]\n"
    stats_text += f" [white]GPU:[/white] {s_donanim['gpu']} [green](x{1 + e['gpu']*0.5})[/green]\n"
    stats_text += f" [white]RAM:[/white] {s_donanim['ram']}\n"
    
    if s_donanim['kits']:
        # Kitleri listelerken çok uzun olup çerçeveyi patlatmasın diye sınırlıyoruz
        kit_liste = ", ".join(s_donanim['kits'])
        if len(kit_liste) > 25: kit_liste = kit_liste[:22] + "..."
        stats_text += f" [white]KİTLER:[/white] {kit_liste}\n"
    
    stats_text += "\n[bold magenta]DarkNet Görev Panosu:[/bold magenta]\n"
    for h in hedefler:
        durum = "[bold green][x][/bold green]" if h["id"] in tamamlanan_gorevler else "[white][ ][/white]"
        kilit = "[bold red](KİLİTLİ)[/bold red] " if stats["level"] < h.get("min_level", 1) else ""
        stats_text += f"{durum} {kilit}{h['baslik'][:20]}\n"
    
    # Rich Panel artık uzunluğu otomatik ve doğru hesaplayacak
    layout["stats"].update(Panel(stats_text, title="[ Sistem & Oyuncu Statüsü ]", border_style="green"))
    
    # Logların zaten Rich stiline (bold green vb.) sahip olduğunu varsayıyorum
    log_text = "\n".join(logs)
    layout["logs"].update(Panel(log_text, title="[ Ağ Trafik Analizi ]", border_style="blue"))
    
    return layout

def baslat():
    ekrani_temizle()
    t = threading.Thread(target=socket_dinleyici, daemon=True)
    t.start()
    try:
        with Live(ekrani_olustur(), refresh_per_second=4) as live:
            while True:
                import random
                stats["cpu_load"] = f"{random.randint(5, 85)}%"
                time.sleep(0.25)
                live.update(ekrani_olustur())
    except KeyboardInterrupt:
        oyunu_kaydet()
        print("\n[!] YagYz C2 güvenli bir şekilde kapatılıyor. Veriler diske yazıldı.")

if __name__ == '__main__':
    baslat()