import sys
import time
import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
JSON_YOLU = BASE_DIR / 'data' / 'missions.json'
SAVE_YOLU = BASE_DIR / 'data' / 'savegame.json'
NOTES_YOLU = BASE_DIR / 'data' / 'notlar.txt'

def ekrani_temizle():
    os.system('clear')

def animasyonlu_yazdir(metin, gecikme=0.03):
    for karakter in metin:
        sys.stdout.write(karakter)
        sys.stdout.flush()
        time.sleep(gecikme)
    print()

def banner_yazdir():
    banner = """\033[1;31m
     __  __             __   __    
     \ \/ /__ _ __ _    \ \ / /____
      \  / _` / _` |_____\ V /_  / 
      / / (_| \__, |_____|| | / /  
     /_/ \__,_|___/       |_|/___| 
    \033[0m"""
    print(banner)
    print("\033[1;36m[+] YagYz Sızma ve Keşif Aracı v6.0 - [Modüler Çekirdek & VulnScan]\033[0m\n")

def json_oku():
    try:
        with open(JSON_YOLU, 'r', encoding='utf-8') as f:
            return json.load(f)["gorevler"]
    except FileNotFoundError:
        print(f"\033[1;31mHATA: {JSON_YOLU} bulunamadı!\033[0m")
        return []

def kayit_oku():
    if SAVE_YOLU.exists():
        try:
            with open(SAVE_YOLU, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {"stats": {"level": 1}, "tamamlanan_gorevler": []}