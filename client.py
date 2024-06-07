import socket
import time

def main():
    server_host = "127.0.0.1"
    server_port = 8888

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_sock:
        i = 0
        while True:
            message = b"Hello, server!"
            client_sock.sendto(message, (server_host, server_port))
            i = i + 1
            # time.sleep(0.001)
            if i == 100000:
                break

if __name__ == "__main__":
    main()
