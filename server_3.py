import socket

def main():
    host = "127.0.0.1"
    port = 8888
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:
        server_sock.bind((host, port))
        while True:
            data, client_addr = server_sock.recvfrom(1024)
            print("接收到来自", client_addr, "的消息:", data.decode())
            ack_message = "ACK".encode()
            server_sock.sendto(ack_message, client_addr)

if __name__ == "__main__":
    main()
