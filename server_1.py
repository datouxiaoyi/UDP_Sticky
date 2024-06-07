import socket
import time

def main():
    host = "127.0.0.1"
    port = 8888
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:
        server_sock.bind((host, port))
        i= 0
        while True:
            data, client_addr = server_sock.recvfrom(1024)
            print("接收来自", client_addr, "的消息:", data.decode())
            if i==0:
                time.sleep(10)
            i+=1
            print(i)

if __name__ == "__main__":
    main()