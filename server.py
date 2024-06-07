from multiprocessing import Queue
import socket
import time
from  multiprocessing import Process

def task(data_list:Queue):
    '''模拟处理处理'''
    while True:
        data = data_list.get()
        time.sleep(3)
     
def main():
    host = "127.0.0.1"
    port = 8888
    data_list = Queue()
    i= 0
    work = Process(target=task, args=(data_list,))
    work.daemon = True
    work.start()    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:
        server_sock.bind((host, port))
        while True:
            data, _ = server_sock.recvfrom(1024)
            data_list.put(data)
            i+=1
            print(i)

if __name__ == "__main__":
    main()