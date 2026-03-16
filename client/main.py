import socket
import time
import sys
import os
from utils import *
from sandbox import VirtualSandbox
from market import market_menu

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
    
def sure_hesapla(baz_sure, parca_tipi, stats):
    # Envanterden ilgili parçanın tier'ını al (yoksa 0)
    tier = stats.get("envanter", {}).get(parca_tipi, 0)
    
    # Her tier hızı %50 artırır (süreyi düşürür)
    carpan = 0.5 
    yeni_sure = baz_sure / (1 + (tier * carpan))
    
    return yeni_sure

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
                
        elif komut == 'market':
            # Sunucudan güncel statları almak için bir sinyal gönderilebilir 
            # veya mevcut stats ile devam edilebilir.
            market_menu(client_socket, kayit_oku()["stats"], sandbox)

        # Stats gösterimi için (isteğe bağlı) yeni bir komut:
        elif komut == 'system':
            s = kayit_oku()["stats"]
            print("\n\033[1;36m=== YagYz SİSTEM BİLEŞENLERİ ===\033[0m")
            print(f"CPU: {s.get('donanim', {}).get('cpu', 'Standart')}")
            print(f"RAM: {s.get('donanim', {}).get('ram', '8GB')}")
            print(f"YÜKLÜ KİTLER: {', '.join(s.get('donanim', {}).get('kits', []))}")
            print("="*30 + "\n")

        elif komut == 'nmap':
            if len(parcalar) < 2:
                print("\033[1;31m[!] Kullanım: nmap <hedef_ip>\033[0m")
                continue
            
            hedef_ip = parcalar[1]
            s = kayit_oku()["stats"]
            cpu_tier = s.get("envanter", {}).get("cpu", 0)
            
            # Donanım bazlı hız hesaplama
            bekleme = 5 / (1 + (cpu_tier * 0.5))
            
            print(f"\033[1;34m[*] Starting Nmap 7.92 ( https://nmap.org ) at {time.strftime('%Y-%m-%d %H:%M')}\033[0m")
            print(f"\033[1;30m[*] Scanning {hedef_ip} [CPU Tier {cpu_tier}]...\033[0m")
            
            # Görsel tarama barı
            bar_uzunluk = 20
            for i in range(bar_uzunluk + 1):
                yuzde = int((i / bar_uzunluk) * 100)
                doluluk = "█" * i
                bosluk = " " * (bar_uzunluk - i)
                print(f"\r\033[1;30m    [{doluluk}{bosluk}] %{yuzde}\033[0m", end="", flush=True)
                time.sleep(bekleme / bar_uzunluk)
            print("\n")

            hedef_data = next((h for h in hedefler if h["hedef_ip"] == hedef_ip), None)
            
            if hedef_data:
                print(f"\033[1;32mNmap scan report for {hedef_ip}\033[0m")
                print("\033[1;37mHost is up (0.00042s latency).\033[0m")
                print("\033[1;34mPORT      STATE   SERVICE\033[0m")
                print("\033[1;30m---------- ------- -------\033[0m")
                
                acik_portlar = hedef_data.get('acik_portlar', [])
                
                if (sandbox.virtual_root / "deep_scan.bin").exists():
                    print("\033[1;35m[*] DeepPacket-Analyzer devrede: Gizli servisler aranıyor...\033[0m")
                    # Gizli portları da ekle (Missions.json'da gizli_portlar diye bir alan açabiliriz)
                    acik_portlar += hedef_data.get('gizli_portlar', [])
                
                if not acik_portlar:
                    print("\033[1;31mNo open ports found on this target.\033[0m")
                else:
                    for p in acik_portlar:
                        servis = "http" if p == "80" else "https" if p == "443" else "microsoft-ds" if p == "445" else "ssh" if p == "22" else "unknown"
                        
                        # WAF (Güvenlik Duvarı) ve Bypass Durum Kontrolü
                        if (hedef_ip, p) in asilan_duvarlar:
                            durum = "\033[1;33mopen (WAF BYPASSED)\033[0m"
                            
                        elif p in hedef_data.get("korumali_portlar", []):
                            durum = "\033[1;31mfiltered (WAF ACTIVE)\033[0m"
                            
                        else:
                            durum = "\033[1;37mopen\033[0m"
                            
                        print(f"\033[1;32m{p}/tcp\033[0m".ljust(19) + durum.ljust(35) + f"\033[1;36m{servis}\033[0m")
                
                if cpu_tier == 0:
                    print("\n\033[1;33m[!] NOTE: CPU Tier 0 detected. Deep scan disabled.\033[0m")
                
                # Sunucuya log gönder
                client_socket.send(f"TARAMA_YAPILDI {hedef_ip}".encode('utf-8'))
                print("\033[1;34m\nNmap done: 1 IP address (1 host up) scanned.\033[0m")
            else:
                print(f"\033[1;31m[!] Failed to resolve '{hedef_ip}'. Target might be down or protected.\033[0m")

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
                print("\033[1;31m[!] Kullanım: exploit <ip> <port> <CVE>\033[0m")
                continue
                
            ip, port, cve = parcalar[1], parcalar[2], parcalar[3].upper()
            s = kayit_oku()["stats"]
            gpu_tier = s.get("envanter", {}).get("gpu", 0)
            
            # Formül: 10 saniye baz süre, GPU Tier arttıkça süre düşer
            bekleme = 10 / (1 + (gpu_tier * 0.7))
            
            print(f"\n\033[1;31m[!] DİKKAT: Exploit başlatılıyor! Hedef: {ip}:{port}\033[0m")
            print(f"\033[1;35m[*] GPU Tier {gpu_tier} aktif. Payload paketleri hazırlanıyor...\033[0m")
            
            # Dinamik İlerleme Barı (Nmap ile uyumlu tasarım)
            bar_uzunluk = 25
            for i in range(bar_uzunluk + 1):
                yuzde = int((i / bar_uzunluk) * 100)
                doluluk = "█" * i
                bosluk = " " * (bar_uzunluk - i)
                print(f"\r\033[1;31m    [{doluluk}{bosluk}] %{yuzde} Payload Injecting...\033[0m", end="", flush=True)
                time.sleep(bekleme / bar_uzunluk)
            print("\n")

            hedef_data = next((h for h in hedefler if h["hedef_ip"] == ip), None)
            
            # Hata çözümü: 'port' yerine 'acik_portlar' listesini kontrol ediyoruz
            if hedef_data and port in [str(p) for p in hedef_data.get('acik_portlar', [])]:
                
                # Zafiyet (CVE) kontrolü
                gercek_cve = hedef_data.get('zafiyetler', {}).get(port)
                
                if gercek_cve == cve:
                    if ip not in sömürülen_sistemler: sömürülen_sistemler.append(ip)
                    
                    print(f"\033[1;32m[+] SUCCESS: Exploit başarıyla tamamlandı.\033[0m")
                    print(f"\033[1;32m[+] CVE: {cve} açığı üzerinden sızıldı.\033[0m")
                    
                    kullanici = hedef_data.get('kullanici_adi', 'root')
                    sifre = hedef_data.get('sifre', 'unknown')
                    print(f"\033[1;33m[*] HASH DUMP: Sistemden kimlik bilgileri çekiliyor...\033[0m")
                    time.sleep(1)
                    print(f"\033[1;36m[+] KİMLİK BULUNDU -> Kullanıcı: {kullanici} | Şifre: {sifre}\033[0m")
                    
                    client_socket.send(f"SIZMA_BASARILI {ip}".encode('utf-8'))
                else:
                    print(f"\033[1;31m[-] FAILURE: Yanlış CVE kodu! Hedef bu zafiyete karşı korumalı.\033[0m")
                    print(f"\033[1;33m[İpucu] 'vulnscan {ip} {port}' yaparak gerçek açığı öğrenin.\033[0m")
            else:
                print(f"\033[1;31m[-] FAILURE: Bağlantı hatası! {ip}:{port} üzerinde exploit edilecek açık bir port bulunamadı.\033[0m")

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