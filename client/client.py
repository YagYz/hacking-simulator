import socket
import time
import sys

def animasyonlu_yazdir(metin, gecikme=0.03):
    """Terminalde Matrix vari harf harf yazılma efekti verir"""
    for karakter in metin:
        sys.stdout.write(karakter)
        sys.stdout.flush()
        time.sleep(gecikme)
    print()

def baslat_hacker_client():
    host = '127.0.0.1'
    port = 5555
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((host, port))
        animasyonlu_yazdir("[+] OPAFD_C2 Ana Sunucusuna güvenli tünel oluşturuldu.", 0.05)
        animasyonlu_yazdir("[!] Sızma araçları yüklendi. Komut bekleniyor...\n", 0.05)
    except ConnectionRefusedError:
        print("HATA: Ana sistem kapalı!")
        return

    while True:
        girdi = input("root@kali:~# ").strip()
        if not girdi:
            continue
            
        parcalar = girdi.split()
        komut = parcalar[0].lower()

        if komut == 'exit':
            animasyonlu_yazdir("Bağlantı sonlandırılıyor...")
            break
            
        # 1. NMAP
        elif komut == 'nmap':
            if len(parcalar) < 2:
                print("Kullanım: nmap <hehef_ip>")
                continue
            hedef = parcalar[1]
            animasyonlu_yazdir(f"[*] {hedef} üzerinde port taraması başlatılıyor...", 0.02)
            time.sleep(1)
            print(f"[+] 80/tcp açık (http)")
            print(f"[+] 22/tcp açık (ssh)")
            
            client_socket.send(f"TARAMA_YAPILDI {hedef}".encode('utf-8'))

        # 2. Sızma CRACK
        elif komut == 'crack':
            if len(parcalar) < 3:
                print("Kullanım: crack <hedef_ip> <port>")
                continue
            hedef = parcalar[1]
            hedef_port = parcalar[2]
            animasyonlu_yazdir(f"[*] {hedef}:{hedef_port} servisine kaba kuvvet (brute-force) saldırısı başlatıldı...")
            
            for i in range(1, 101, 20):
                sys.stdout.write(f"\rİlerleyiş: [%{i}]")
                sys.stdout.flush()
                time.sleep(0.4)
            print("\n[+] Erişim Sağlandı! (Kullanıcı: admin, Şifre: root123)")
            
            client_socket.send(f"SIZMA_BASARILI {hedef}".encode('utf-8'))

        else:
            print(f"bash: {komut}: komut bulunamadı. (Kullanılabilir: nmap, crack, exit)")

    client_socket.close()

if __name__ == '__main__':
    baslat_hacker_client()