import socket
import time

def main():
    server_host = "127.0.0.1"
    server_port = 8888
    message = ["Hello, server!"]*10
    timeout = 2 
    i = 0

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_sock:
        client_sock.settimeout(timeout)
        while i<len(message):
            try:
                client_sock.sendto(message[i].encode(), (server_host, server_port))
                print(f"发送消息: {message[i]}--{i}")
                ack, _ = client_sock.recvfrom(1024)
                if ack.decode() == "ACK":
                    print("接收到确认消息: ACK")
                    i+=1
                    continue
            except socket.timeout:
                print(f"未接收到确认消息，重传数据包")
            time.sleep(1)

if __name__ == "__main__":
    main()
