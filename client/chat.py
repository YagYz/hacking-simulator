import json
from pathlib import Path
from utils import ekrani_temizle, banner_yazdir

BASE_DIR = Path(__file__).resolve().parent.parent
MSG_JSON = BASE_DIR / 'data' / 'messages.json'
SAVE_YOLU = BASE_DIR / 'data' / 'savegame.json'

def guncel_kaydi_getir():
    """Diskten her zaman en taze veriyi çeker"""
    try:
        with open(SAVE_YOLU, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"stats": {}, "tamamlanan_gorevler": []}
    
def mesajlari_getir():
    try:
        with open(MSG_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)["mesajlar"]
    except: return []

def kilit_acik_mi(trigger, stats, sandbox):
    """Event-Driven kontrol mekanizması"""
    if trigger["tip"] == "baslangic": 
        return True
    elif trigger["tip"] == "seviye" and stats.get("level", 1) >= trigger["deger"]: 
        return True
    elif trigger["tip"] == "esya" and (sandbox.virtual_root / trigger["deger"]).exists(): 
        return True
    elif trigger["tip"] == "bakiye" and stats.get("bakiye", 0) >= trigger["deger"]:
        return True
    elif trigger["tip"] == "gorev_tamamlandi":
        taze_kayit = guncel_kaydi_getir() # Diskten taze veriyi çek
        tamamlananlar = taze_kayit.get("tamamlanan_gorevler", [])
        if trigger["deger"] in tamamlananlar:
            return True
    # İleride "gorev_tamamlandi" gibi yeni triggerlar da buraya eklenecek
    return False

def bildirim_kontrol(stats, sandbox):
    """Ana terminalde okunmamış mesaj sayısını döndürür"""
    mesajlar = mesajlari_getir()
    
    # Okunan mesajları da taze kayıttan garantiye alalım
    taze_kayit = guncel_kaydi_getir()
    okunanlar = taze_kayit.get("stats", {}).get("okunan_mesajlar", [])
    
    yeni_mesaj_sayisi = 0
    
    for m in mesajlar:
        if m["id"] not in okunanlar and kilit_acik_mi(m["trigger"], stats, sandbox):
            yeni_mesaj_sayisi += 1
            
    return yeni_mesaj_sayisi

def chat_menu(stats, sandbox, client_socket):
    mesajlar = mesajlari_getir()
    
    while True:
        # 1. HER DÖNGÜDE VERİYİ TAZELE (Senkronizasyon sorunu kökten çözüldü)
        taze_kayit = guncel_kaydi_getir()
        guncel_stats = taze_kayit.get("stats", {})
        okunanlar = guncel_stats.get("okunan_mesajlar", [])
        tamamlananlar = taze_kayit.get("tamamlanan_gorevler", [])
        aktifler = guncel_stats.get("aktif_gorevler", [])
        
        ekrani_temizle()
        # banner_yazdir() # Eğer banner fonksiyonun varsa buraya ekle
        print("\033[1;36m" + "="*50)
        print("      [ YagYz SECURE MESSENGER v1.0 ]")
        print("="*50 + "\033[0m\n")
        
        gosterilen_mesajlar = []
        for i, m in enumerate(mesajlar):
            if kilit_acik_mi(m["trigger"], guncel_stats, sandbox):
                gosterilen_mesajlar.append(m)
                # Yeni mesaj etiketi artık taze veriyle belirleniyor
                durum = " \033[1;32m[YENİ]\033[0m" if m["id"] not in okunanlar else " \033[1;30m[Okundu]\033[0m"
                print(f"\033[1;37m[{len(gosterilen_mesajlar)}] {durum} {m['gonderen']} - {m['konu']}\033[0m")
                
        print("\n\033[1;33m[Geri dönmek için 'exit' veya 'q' yazın]\033[0m")
        secim = input("\nOkumak istediğiniz mesaj no: ").strip()
        
        if secim.lower() in ['exit', 'q']: break
        
        if secim.isdigit() and 1 <= int(secim) <= len(gosterilen_mesajlar):
            secili_mesaj = gosterilen_mesajlar[int(secim)-1]
            
            # Sunucuya mesajın okunduğunu bildir
            if secili_mesaj["id"] not in okunanlar:
                try:
                    client_socket.send(f"MESAJ_OKUNDU {secili_mesaj['id']}".encode('utf-8'))
                except: pass
            
            ekrani_temizle()
            print("\033[1;36m" + "-"*50)
            print(f"KİMDEN : {secili_mesaj['gonderen']}")
            print(f"KONU   : {secili_mesaj['konu']}")
            print("-" * 50 + "\033[0m\n")
            print(f"\033[1;37m{secili_mesaj['icerik']}\033[0m\n")
            
            # --- GÖREV KONTROLÜ (TAZE VERİ İLE) ---
            if "gorev_id" in secili_mesaj:
                g_id = secili_mesaj["gorev_id"]
                
                if g_id in tamamlananlar:
                    print("\033[1;32m[+] BİLGİ: Bu operasyon zaten başarıyla tamamlandı.\033[0m")
                elif g_id in aktifler:
                    print("\033[1;36m[*] SİSTEM NOTU: Bu operasyon C2 panosunda aktif. (Detaylar için 'targets' yazın)\033[0m")
                else:
                    print("\033[1;35m[!] EKLENTİ: Bu mesaj şifreli bir hedef dosyası içeriyor.\033[0m")
                    kabul = input("\033[1;33mGörevi sistemine indirmek ister misin? (E/H): \033[0m").strip().lower()
                    
                    if kabul == 'e':
                        try:
                            client_socket.send(f"GOREV_KABUL {g_id}".encode('utf-8'))
                            print("\033[1;32m[+] Hedef dosyası indirildi. C2 panosuna eklendi.\033[0m")
                            import time; time.sleep(1) # Dosyanın diske yazılması için ufak bir bekleme
                        except Exception as e:
                            print(f"\033[1;31m[-] Bağlantı hatası: {e}\033[0m")
            # ------------------------------------
            
            print("\033[1;36m" + "-"*50 + "\033[0m")
            input("\033[1;33mGeri dönmek için Enter'a bas...\033[0m")
        else:
            print("\033[1;31m[-] Geçersiz seçim!\033[0m")
            import time; time.sleep(1)