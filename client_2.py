import socket

def calculate_parity(data):
    '''计算奇偶检验码'''
    parity = sum(bytearray(data)) % 256
    return parity

def main():
    server_host = "127.0.0.1"
    server_port = 8888
    message = "Hello, server!"  
    message_bytes = message.encode()
    parity_byte = calculate_parity(message_bytes)
    packet = message_bytes + parity_byte

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_sock:
        while True:
            client_sock.sendto(packet, (server_host, server_port))
            print(f"发送消息: {message}")
            client_sock.settimeout(3)
            try:
                ack, _ = client_sock.recvfrom(1024)
                if ack.decode() == "True":
                    print("数据已成功接收")
                    break
                else:
                    print("数据破损，重传中...")
            except socket.timeout:
                print("超时，重传中...")

if __name__ == "__main__":
    main()
