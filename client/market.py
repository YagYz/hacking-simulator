import time
import json
import re
from pathlib import Path
from utils import ekrani_temizle, banner_yazdir

BASE_DIR = Path(__file__).resolve().parent.parent
MARKET_JSON = BASE_DIR / 'data' / 'market.json'

def market_listele():
    """Market veritabanını okur."""
    try:
        with open(MARKET_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)["urunler"]
    except Exception as e:
        print(f"Market verisi okunamadı: {e}")
        return []

def temiz_yazi(metin):
    """Renk kodlarını temizleyerek gerçek uzunluğu bulur."""
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', metin)

def market_menu(client_socket, current_stats, sandbox):
    urunler = market_listele()
    # Mevcut envanter seviyelerini al (Yoksa 0 kabul et)
    envanter = current_stats.get("envanter", {"cpu": 0, "gpu": 0, "ram": 0})
    
    while True:
        ekrani_temizle()
        banner_yazdir()
        
        bakiye = current_stats.get('bakiye', 0)
        print(f"\033[1;32mMEVCUT BAKİYE: ${bakiye}\033[0m")
        print("\033[1;37m" + "─"*75 + "\033[0m")
        
        # --- FİLTRELEME MANTIĞI ---
        gosterilecekler = []
        for u in urunler:
            if u['tip'] == 'donanim':
                # Sadece mevcut seviyenin tam bir üstünü göster (Tier Progress)
                mevcut_seviye = envanter.get(u['parca'], 0)
                if u['tier'] == mevcut_seviye + 1:
                    gosterilecekler.append(u)
            else:
                # Kitler (yazılımlar) her zaman listelenir
                gosterilecekler.append(u)

        if not gosterilecekler:
            print("\n\033[1;33m[!] Market şu an boş veya tüm donanımlar maksimum seviyede.\033[0m")
        else:
            print(f"\033[1;34m{'ID':<10} {'ÜRÜN ADI':<25} {'FİYAT':<10} {'AÇIKLAMA'}\033[0m")
            print("-" * 75)
            for u in gosterilecekler:
                print(f"\033[1;37m{u['id']:<10} {u['isim']:<25} ${u['fiyat']:<9} {u['aciklama']}\033[0m")

        print("\033[1;37m" + "─"*75 + "\033[0m")
        print("\033[1;33m[Geri dönmek için 'exit' yazın]\033[0m")
        
        secim = input("\nSatın almak istediğiniz Ürün ID: ").strip().upper()
        
        if secim == 'EXIT':
            break
            
        secili_urun = next((u for u in gosterilecekler if u['id'].upper() == secim), None)
        
        if secili_urun:
            if bakiye >= secili_urun['fiyat']:
                # Sunucuya detaylı satın alma isteği gönder
                # Format: SATIN_ALMA <fiyat> <tip> <id> <isim>
                istek = f"SATIN_ALMA {secili_urun['fiyat']} {secili_urun['tip']} {secili_urun['id']} {secili_urun['isim']}"
                client_socket.send(istek.encode('utf-8'))
                
                # Sunucudan onay bekle
                cevap = client_socket.recv(1024).decode('utf-8')
                
                if cevap == "ONAY":
                    print(f"\n\033[1;32m[+] İŞLEM BAŞARILI: {secili_urun['isim']} envantere eklendi.\033[0m")
                    
                    # Eğer ürün bir 'kit' ise yerel sanal makineye (Sandbox) dosya olarak oluştur
                    if secili_urun['tip'] == 'kit':
                        kit_dosyası = sandbox.virtual_root / secili_urun['dosya']
                        kit_dosyası.touch()
                        print(f"\033[1;36m[*] {secili_urun['dosya']} yerel sistem dizinine yüklendi.\033[0m")
                    
                    # Yerel bakiye ve envanteri anlık güncelle (Döngü devam ederken doğru görünsün)
                    current_stats['bakiye'] -= secili_urun['fiyat']
                    if secili_urun['tip'] == 'donanim':
                        envanter[secili_urun['parca']] = secili_urun['tier']
                    
                    time.sleep(2)
                elif cevap == "ZATEN_SAHIP":
                    print("\033[1;31m[-] Bu donanıma zaten sahipsiniz veya daha üst modelini kullanıyorsunuz.\033[0m")
                    time.sleep(2)
                else:
                    print("\033[1;31m[-] HATA: Bakiye yetersiz veya sunucu işlemi reddetti.\033[0m")
                    time.sleep(2)
            else:
                print("\033[1;31m[-] Yetersiz bakiye! Daha fazla görev tamamlamalısın.\033[0m")
                time.sleep(2)
        else:
            print("\033[1;31m[-] Geçersiz ID. Lütfen listedeki bir ID'yi girin.\033[0m")
            time.sleep(1.5)