import json
from pathlib import Path
from utils import ekrani_temizle, banner_yazdir

BASE_DIR = Path(__file__).resolve().parent.parent
MSG_JSON = BASE_DIR / 'data' / 'messages.json'

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
    # İleride "gorev_tamamlandi" gibi yeni triggerlar da buraya eklenecek
    return False

def bildirim_kontrol(stats, sandbox):
    """Ana terminalde okunmamış mesaj sayısını döndürür"""
    mesajlar = mesajlari_getir()
    okunanlar = stats.get("okunan_mesajlar", [])
    yeni_mesaj_sayisi = 0
    
    for m in mesajlar:
        if m["id"] not in okunanlar and kilit_acik_mi(m["trigger"], stats, sandbox):
            yeni_mesaj_sayisi += 1
            
    return yeni_mesaj_sayisi

def chat_menu(stats, sandbox, client_socket):
    mesajlar = mesajlari_getir()
    if "okunan_mesajlar" not in stats:
        stats["okunan_mesajlar"] = []
        
    while True:
        ekrani_temizle()
        banner_yazdir()
        print("\033[1;36m" + "="*50)
        print("      [ YagYz SECURE MESSENGER v1.0 ]")
        print("="*50 + "\033[0m\n")
        
        gosterilen_mesajlar = []
        for i, m in enumerate(mesajlar):
            if kilit_acik_mi(m["trigger"], stats, sandbox):
                gosterilen_mesajlar.append(m)
                durum = " \033[1;32m[YENİ]\033[0m" if m["id"] not in stats["okunan_mesajlar"] else " \033[1;30m[Okundu]\033[0m"
                print(f"\033[1;37m[{len(gosterilen_mesajlar)}] {durum} {m['gonderen']} - {m['konu']}\033[0m")
                
        print("\n\033[1;33m[Geri dönmek için 'exit' veya 'q' yazın]\033[0m")
        secim = input("\nOkumak istediğiniz mesaj no: ").strip()
        
        if secim.lower() in ['exit', 'q']: break
        
        if secim.isdigit() and 1 <= int(secim) <= len(gosterilen_mesajlar):
            secili_mesaj = gosterilen_mesajlar[int(secim)-1]
            
            # Mesajı okundu olarak işaretle ve diske kaydet
            if secili_mesaj["id"] not in stats["okunan_mesajlar"]:
                stats["okunan_mesajlar"].append(secili_mesaj["id"]) # Yerel belleği güncelle
                try:
                    # Sunucuya mesajın okunduğunu bildir, o diske yazsın
                    client_socket.send(f"MESAJ_OKUNDU {secili_mesaj['id']}".encode('utf-8'))
                except Exception as e:
                    print(f"\033[1;31m[-] Sunucu bağlantı hatası: {e}\033[0m")
            
            # Mesaj İçeriği Ekranı
            ekrani_temizle()
            print("\033[1;36m" + "-"*50)
            print(f"KİMDEN : {secili_mesaj['gonderen']}")
            print(f"KONU   : {secili_mesaj['konu']}")
            print("-" * 50 + "\033[0m\n")
            print(f"\033[1;37m{secili_mesaj['icerik']}\033[0m\n")
            print("\033[1;36m" + "-"*50 + "\033[0m")
            input("\033[1;33mGeri dönmek için Enter'a bas...\033[0m")
        else:
            print("\033[1;31m[-] Geçersiz seçim!\033[0m")
            import time; time.sleep(1)