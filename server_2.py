import socket

def verify_and_correct(data):
    '''检验奇偶检验码'''
    received_data = data[:-1]
    received_parity = data[-1]
    calculated_parity = sum(bytearray(received_data)) % 256

    if calculated_parity == received_parity:
        return received_data.decode(), True
    else:
        return None, False
def main():
    host = "127.0.0.1"
    port = 8888
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:
        server_sock.bind((host, port))
        while True:
            data, client_addr = server_sock.recvfrom(1024)
            message, is_correct = verify_and_correct(data)
            if is_correct:
                print("接收到来自", client_addr, "的消息:", message)
                ack_message = "True".encode()
                server_sock.sendto(ack_message, client_addr)                   
            else:
                print("接收到来自", client_addr, "的错误消息")
                ack_message = "False".encode()
                server_sock.sendto(ack_message, client_addr)                

if __name__ == "__main__":
    main()
