import os
from pathlib import Path
from utils import animasyonlu_yazdir

class VirtualSandbox:
    def __init__(self, base_dir):
        self.virtual_root = base_dir / 'local_machine'
        self.virtual_root.mkdir(exist_ok=True)
        self.current_dir = self.virtual_root
        os.chdir(self.current_dir)

    def get_prompt_path(self):
        goreceli_yol = self.current_dir.relative_to(self.virtual_root)
        return "~" if str(goreceli_yol) == "." else f"~/{goreceli_yol}"

    def yerel_komut_calistir(self, komut, parcalar):
        if komut == 'ls':
            for d in os.listdir(self.current_dir):
                tam_yol = self.current_dir / d
                renk = "\033[1;34m" if tam_yol.is_dir() else "\033[1;32m"
                print(f"{renk}{d}\033[0m", end="  ")
            print()
            
        elif komut == 'cd':
            hedef = parcalar[1] if len(parcalar) > 1 else str(self.virtual_root)
            if hedef.startswith('~'): hedef = hedef.replace('~', str(self.virtual_root), 1)
            yeni_hedef = (self.current_dir / hedef).resolve()
            
            if self.virtual_root in yeni_hedef.parents or yeni_hedef == self.virtual_root:
                if yeni_hedef.is_dir():
                    self.current_dir = yeni_hedef
                    os.chdir(self.current_dir)
                else: print(f"bash: cd: {parcalar[1]}: Bir dizin değil")
            else: print(f"\033[1;31mbash: cd: {parcalar[1]}: Erişim reddedildi!\033[0m")
            
        elif komut == 'rm':
            if len(parcalar) < 2: return print("rm: eksik işlenen")
            hedef_dosya = parcalar[1]
            hedef_yol = (self.current_dir / hedef_dosya).resolve()
            
            if self.virtual_root in hedef_yol.parents and hedef_yol.exists():
                if hedef_yol.is_dir(): print(f"rm: '{hedef_dosya}' silinemedi: Bu bir dizin")
                else:
                    hedef_yol.unlink()
                    print(f"\033[1;32m[+] Yerel dosya silindi: {hedef_dosya}\033[0m")
            else: print(f"rm: '{hedef_dosya}': Dosya bulunamadı veya yetki yok!")

    def ssh_baslat(self, kullanici, hedef_ip, hedef_data, client_socket):
        girilen_sifre = input(f"{kullanici}@{hedef_ip}'s password: ")
        if girilen_sifre != hedef_data.get("sifre"):
            return print("\033[1;31mPermission denied (publickey,password).\033[0m")
            
        print("\033[1;32m[+] Uzak sunucuya güvenli bağlantı kuruldu.\033[0m")
        uzak_fs = hedef_data.get("dosya_sistemi", {"/": []})
        uzak_dir = "/"
        log_silindi = False
        
        while True:
            ssh_girdi = input(f"\033[1;31m{kullanici}@{hedef_ip}\033[0m:\033[1;34m{uzak_dir}\033[0m$ ").strip()
            if not ssh_girdi: continue
            ssh_parca = ssh_girdi.split()
            ssh_komut = ssh_parca[0].lower()
            
            if ssh_komut == "exit":
                print("\033[1;33mBağlantı kapatılıyor...\033[0m")
                if not log_silindi:
                    print("\033[1;41m[ POLİS UYARISI ] İzler (/var/log/auth.log) silinmedi! Risk altındasınız.\033[0m")
                break
            elif ssh_komut == "ls":
                print("  ".join(uzak_fs.get(uzak_dir, [])))
            elif ssh_komut == "cd":
                if len(ssh_parca) < 2: continue
                git = ssh_parca[1]
                if git == "..":
                    if uzak_dir != "/":
                        uzak_dir = "/" + "/".join(uzak_dir.strip('/').split('/')[:-1])
                        if uzak_dir == "/": uzak_dir = "/"
                else:
                    yeni_dir = uzak_dir + ("/" if uzak_dir != "/" else "") + git
                    if yeni_dir in uzak_fs: uzak_dir = yeni_dir
                    else: print(f"bash: cd: {git}: Böyle bir dosya ya da dizin yok")
            elif ssh_komut == "download":
                if len(ssh_parca) < 2: continue
                dosya = ssh_parca[1]
                if dosya in uzak_fs.get(uzak_dir, []):
                    animasyonlu_yazdir(f"[*] {dosya} indiriliyor...")
                    (self.current_dir / dosya).touch() # Sandbox'a dosyayı oluştur
                    client_socket.send(f"DOSYA_INDIRILDI {hedef_ip} {dosya}".encode('utf-8'))
                    print(f"\033[1;32m[+] Dosya yerel makineye çekildi: {dosya}\033[0m")
                else: print(f"Hata: {dosya} bulunamadı.")
            elif ssh_komut == "rm":
                if len(ssh_parca) < 2: continue
                dosya = ssh_parca[1]
                if dosya in uzak_fs.get(uzak_dir, []):
                    uzak_fs[uzak_dir].remove(dosya)
                    print(f"[{dosya}] silindi.")
                    if dosya == "auth.log":
                        log_silindi = True
                        print("\033[1;32m[+] Loglar temizlendi. Güvendesiniz.\033[0m")
                else: print(f"rm: '{dosya}': Böyle bir dosya yok")
            else: print(f"{ssh_komut}: komut bulunamadı")