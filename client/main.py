import socket
import time
import sys
import os
from utils import *
from sandbox import VirtualSandbox

try: import readline
except ImportError: pass

def yardim_menusu():
    print("\n" + "="*60)
    print("\033[1;31m  YagYz SIZMA TESTİ & DARKNET OPERASYON KILAVUZU v6.0\033[0m")
    print("="*60)
    
    print("\n\033[1;36m[ AŞAMA 1: KEŞİF VE TARAMA ]\033[0m")
    print(f"  \033[1;32mnmap <ip>\033[0m            : Hedefteki tüm kapıları (portları) listeler.")
    print(f"  \033[1;32mvulnscan <ip> <port>\033[0m : Açık portun zafiyet (CVE) analizini yapar.")
    
    print("\n\033[1;36m[ AŞAMA 2: ERİŞİM VE SÖMÜRÜ ]\033[0m")
    print(f"  \033[1;32mbypass <ip> <port>\033[0m   : WAF/Firewall engelini etkisiz hale getirir.")
    print(f"  \033[1;32mexploit <ip> <port> <CVE>\033[0m: Bulunan zafiyeti sömürerek root erişimi alır.")
    
    print("\n\033[1;36m[ AŞAMA 3: SİSTEME GİRİŞ & OPERASYON ]\033[0m")
    print(f"  \033[1;32mssh <user>@<ip>\033[0m      : Exploit edilmiş sisteme terminal bağlantısı kurar.")
    print(f"  \033[1;33m  > download <dosya>\033[0m : (SSH İçinde) Hedef veriyi kendi makinenize çeker.")
    print(f"  \033[1;33m  > rm <dosya>\033[0m       : (SSH İçinde) İzleri silmek için logları temizler.")
    
    print("\n\033[1;36m[ YEREL TERMİNAL & YÖNETİM ]\033[0m")
    print(f"  \033[1;32mmissions\033[0m             : Seviyene uygun güncel DarkNet işlerini listeler.")
    print(f"  \033[1;32maccept <id>\033[0m          : Bir görevi kabul eder ve brifingi görüntüler.")
    print(f"  \033[1;32mls / cd / rm\033[0m         : Kendi sanal makinenizde dosya yönetimi yapar.")
    print(f"  \033[1;32mnano\033[0m                 : İstihbarat notlarını düzenlemek için editörü açar.")
    print(f"  \033[1;32mclear / exit\033[0m         : Ekranı temizler veya güvenli çıkış yapar.")
    print("="*60 + "\n")

def baslat():
    ekrani_temizle()
    banner_yazdir()
    
    hedefler = json_oku()
    sandbox = VirtualSandbox(BASE_DIR)
    
    asilan_duvarlar = [] 
    sömürülen_sistemler = [] # Yeni mekanik: Crack bitti, sömürü (exploit) geldi
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('127.0.0.1', 5555))
        animasyonlu_yazdir("[+] YagYz C2 Bağlantısı: AKTİF", 0.05)
    except ConnectionRefusedError:
        print("\033[1;31mHATA: YagYz C2 Ana sunucusu kapalı!\033[0m")
        return

    while True:
        # Yol göstergesini Sandbox'tan dinamik alıyoruz
        girdi = input(f"\033[1;32mroot@yagyz\033[0m:\033[1;34m{sandbox.get_prompt_path()}\033[0m# ").strip()
        if not girdi: continue
            
        parcalar = girdi.split()
        komut = parcalar[0].lower()

        if komut == 'exit': break
        elif komut == 'help': yardim_menusu()
        elif komut == 'clear':
            ekrani_temizle()
            banner_yazdir()

        # Yerel sandbox komutlarını sandbox sınıfına yolluyoruz! (Kod ne kadar temizlendi bak)
        elif komut in ['ls', 'cd', 'rm']:
            sandbox.yerel_komut_calistir(komut, parcalar)
            
        elif komut == 'nano':
            os.system(f'nano {NOTES_YOLU}')
            ekrani_temizle()
            banner_yazdir()

        elif komut == 'missions':
            kayit = kayit_oku()
            tamamlananlar = kayit.get("tamamlanan_gorevler", [])
            level = kayit.get("stats", {}).get("level", 1)
            uygun_gorevler = [h for h in hedefler if h["id"] not in tamamlananlar and h.get("min_level", 1) <= level]
            
            print("\033[1;35m\n=== AKTİF DARKNET GÖREV PANOSU ===\033[0m")
            if not uygun_gorevler: print("\033[1;33m[!] Şu anda sana uygun yeni bir görev yok.\033[0m\n")
            else:
                for h in uygun_gorevler[:3]:
                    print(f"\033[1;33m[{h['id']}]\033[0m {h['baslik']} (Hedef: {h['hedef_ip']}) - Ödül: ${h['odul']}")
                print()

        elif komut == 'accept':
            if len(parcalar) < 2: 
                print("\033[1;31m[!] Kullanım: accept <Görev_ID>\033[0m")
                continue
                
            gorev_id = parcalar[1].upper()
            kayit = kayit_oku()
            h = next((h for h in hedefler if h["id"] == gorev_id), None)
            
            if h:
                import re
                def temiz_yazi(metin):
                    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', metin)

                ekrani_temizle()
                banner_yazdir()
                
                GNS = 60 # İç genişlik
                
                print("\033[1;37m┌" + "─"*GNS + "┐")
                
                # Başlıkları ve statik satırları yazdır
                bilgiler = [
                    (f"\033[1;31m GÖREV DOSYASI: {h['id']}\033[0m", ""),
                    (f"\033[1;33m BAŞLIK:\033[0m {h['baslik']}", ""),
                    (f"\033[1;33m İSTİHBARAT:\033[0m {h['veren_kisi']}", ""),
                    (f"\033[1;33m HEDEF IP:\033[0m {h['hedef_ip']}", ""),
                    (f"\033[1;32m ÖDÜL:\033[0m ${h['odul']} | \033[1;34mXP:\033[0m +{h['xp']}", "")
                ]

                for renkli, _ in bilgiler:
                    temiz = temiz_yazi(renkli)
                    bosluk = GNS - len(temiz)
                    print(f"│{renkli}" + " "*bosluk + "│")
                
                print("├" + "─"*GNS + "┤")
                
                # Operasyon Detayları Başlığı
                detay_baslik = " \033[1;36m[ OPERASYON DETAYLARI ]\033[0m"
                print(f"│{detay_baslik}" + " "*(GNS - len(temiz_yazi(detay_baslik))) + "│")
                
                # Hikaye (Word Wrap) Mantığı
                kelimeler = h['hikaye'].split()
                satir = " "
                for k in kelimeler:
                    if len(satir + k) < GNS - 2:
                        satir += k + " "
                    else:
                        print(f"│{satir.ljust(GNS)}│")
                        satir = " " + k + " "
                if satir:
                    print(f"│{satir.ljust(GNS)}│")

                print("│" + " "*GNS + "│")
                
                # Eylem Satırı
                eylem = f" \033[1;31mEYLEM:\033[0m {h['istenen_eylem'].upper()}"
                print(f"│{eylem}" + " "*(GNS - len(temiz_yazi(eylem))) + "│")
                
                print("└" + "─"*GNS + "┘\033[0m")
                print("\033[1;35m[*] Görev kabul edildi. Sistemler optimize ediliyor...\033[0m\n")
            else:
                print(f"\033[1;31m[-] HATA: '{gorev_id}' geçersiz.\033[0m")

        elif komut == 'nmap':
            if len(parcalar) < 2: continue
            ip = parcalar[1]
            animasyonlu_yazdir(f"[*] {ip} taranıyor...", 0.02)
            time.sleep(1)
            h = next((h for h in hedefler if h.get("hedef_ip") == ip), None)
            if h:
                for port in h.get("acik_portlar", []):
                    if (ip, port) in asilan_duvarlar: print(f"\033[1;33m[+] {port}/tcp (WAF ÇÖKERTİLDİ)\033[0m")
                    elif port in h.get("korumali_portlar", []): print(f"\033[1;31m[!] {port}/tcp (WAF AKTİF)\033[0m")
                    else: print(f"\033[1;32m[+] {port}/tcp açık\033[0m")
                client_socket.send(f"TARAMA_YAPILDI {ip}".encode('utf-8'))
            else: print("\033[1;31m[-] Host bulunamadı.\033[0m")

        # YENİ MEKANİK: Zafiyet Taraması
        elif komut == 'vulnscan':
            if len(parcalar) < 3: 
                print("Kullanım: vulnscan <hedef_ip> <port>")
                continue
            ip, port = parcalar[1], parcalar[2]
            animasyonlu_yazdir(f"[*] {ip}:{port} üzerinde güvenlik açık taraması yapılıyor...")
            time.sleep(1.5)
            h = next((h for h in hedefler if h.get("hedef_ip") == ip), None)
            if h and port in h.get("acik_portlar", []):
                cve = h.get("zafiyetler", {}).get(port)
                if cve:
                    print(f"\033[1;35m[!] KRİTİK ZAFİYET BULUNDU: {cve}\033[0m (Exploit yazmak için bu kodu kullanın)")
                else:
                    print("\033[1;32m[-] Bu serviste bilinen bir zafiyet (CVE) tespit edilemedi.\033[0m")
            else: print("\033[1;31m[-] Port kapalı veya taranamıyor.\033[0m")

        elif komut == 'bypass':
            if len(parcalar) < 3: continue
            ip, port = parcalar[1], parcalar[2]
            h = next((h for h in hedefler if h.get("hedef_ip") == ip), None)
            if h and port in h.get("korumali_portlar", []):
                animasyonlu_yazdir(f"[*] WAF atlatılıyor...")
                asilan_duvarlar.append((ip, port))
                client_socket.send(f"FIREWALL_BYPASS {ip} {port}".encode('utf-8'))
                print("\033[1;32m[+] Güvenlik duvarı atlatıldı!\033[0m")

        # YENİ MEKANİK: CVE kodu ile Sömürü (Crack yerine)
        elif komut == 'exploit':
            if len(parcalar) < 4:
                print("Kullanım: exploit <hedef_ip> <port> <CVE-Kodu> (Örn: exploit 10.0.1.15 22 CVE-2001-0144)")
                continue
            ip, port, girilen_cve = parcalar[1], parcalar[2], parcalar[3].upper()
            h = next((h for h in hedefler if h.get("hedef_ip") == ip), None)
            
            if h and port in h.get("acik_portlar", []):
                if port in h.get("korumali_portlar", []) and (ip, port) not in asilan_duvarlar:
                    print("\033[1;41m[ CRITICAL ] ERİŞİM REDDEDİLDİ! WAF bağlantıyı kesti.\033[0m")
                    continue
                
                gercek_cve = h.get("zafiyetler", {}).get(port)
                if gercek_cve == girilen_cve:
                    animasyonlu_yazdir(f"[*] {girilen_cve} zafiyeti üzerinden sisteme payload enjekte ediliyor...")
                    time.sleep(1)
                    if ip not in sömürülen_sistemler: sömürülen_sistemler.append(ip)
                    print(f"\033[1;32m[+] Sömürü Başarılı! (SSH: {h.get('kullanici_adi')} / {h.get('sifre')})\033[0m")
                    client_socket.send(f"SIZMA_BASARILI {ip}".encode('utf-8'))
                else:
                    print(f"\033[1;31m[-] EXPLOIT BAŞARISIZ! Hedef sistem {girilen_cve} açığına karşı yamalanmış.\033[0m")
            else: print("\033[1;31m[-] Port kapalı.\033[0m")

        elif komut == 'ssh':
            if len(parcalar) < 2 or '@' not in parcalar[1]: continue
            kullanici, ip = parcalar[1].split('@')
            if ip not in sömürülen_sistemler:
                print("\033[1;31m[-] Bağlantı reddedildi. Önce zafiyeti exploit etmelisiniz.\033[0m")
                continue
            h = next((h for h in hedefler if h.get("hedef_ip") == ip), None)
            if h and kullanici == h.get("kullanici_adi"):
                # Sandbox modülündeki SSH alt döngüsünü çağırıyoruz!
                sandbox.ssh_baslat(kullanici, ip, h, client_socket)
            else: print("\033[1;31mSSH Hatası: Kullanıcı bulunamadı.\033[0m")
        else: print(f"bash: {komut}: komut bulunamadı. (Yardım için 'help' yazın)")

if __name__ == '__main__':
    baslat()