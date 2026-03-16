import socket

def baslat_hacker_client():
    host = '127.0.0.1'
    port = 5555
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((host, port))
        print("Ana sisteme sizildi. Komut girmeye hazir.\n")
    except ConnectionRefusedError:
        print("HATA: Ana Sistem (SERVER) Kapali Yada Bulunamadi!")
        return
    
    while True:
        komut = input("root@kali:~# ")
        
        if komut.lower() == 'exit':
            break
    
        client_socket.send(komut.encode('utf-8'))
        
    client_socket.close()
    
if __name__ == '__main__':
    baslat_hacker_client()