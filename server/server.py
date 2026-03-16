import socket

def baslat_ui_server():
    host = '127.0.0.1'
    port = 5555
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    
    print("=== SISTEM STATUS VE GOREVLERI ===")
    print(f"[{port}] Portu Dinleniyor... Komutlar Bekleniyor.\n")
    
    conn, addr = server_socket.accept()
    print(f"Bilinmeyen Bir Cihaz Baglandi: {addr}\n")
    
    while True:
        data = conn.recv(1024).decode('utf-8')
        if not data:
            break
        
        print(f"[!] SİSTEM ALARMI: Yeni bir eylem algılandı -> {data}")
        
    conn.close()
    
if __name__ == '__main__':
    baslat_ui_server()