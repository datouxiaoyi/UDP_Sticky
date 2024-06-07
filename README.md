# 一、介绍

UDP是一种不可靠的、无连接的、基于数据报的传输层协议。相比于TCP就比较简单，像写信一样，直接打包丢过去，就不用管了，而不用TCP这样的反复确认。所以UDP的优势就是速度快，开销小。但是随之而来的就是不稳定，面向无连接的，无法确认数据包。会导致丢包问题。

![whiteboard_exported_image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/40e51fd2246e473f9bc3902c6ed42155~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1200&h=1000&s=100382&e=png&b=ffffff)

# 二、丢包原因

1、服务未启动或出现故障，但是数据包依然发送出去，目标地址和端口没有任何进程在监听，这些数据包将被丢弃。

2、缓冲区满，数据包溢出丢失。在实际情况中，如果处理的速度比较慢，会导致数据包堆积在缓冲区，当缓冲区满时，发送的数据无处存放就会丢失。另一种情况是发送的数据包非常大时，可能这个数据包直接超出了缓冲区的大小，也会导致数据丢失。最后一种情况和第一种差不多，由于发送的速率过快，导致处理不及时。

**Client**

```python
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
            time.sleep(0.001)
            if i == 100000:
                break

if __name__ == "__main__":
    main()
```

**Serevr**

```python
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
```

这里的客户端发送了100000个数据包，在服务端特意设置处理第一个数据包后停止10秒模拟数据处理时间。在这种情况下，就会因为速度过快，缓冲区满而导致数据包丢失。服务端最后的打印为

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/bf56cb0de324457394070f19bf1ce674~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=451&h=193&s=27622&e=png&b=181818)

可以看到只接收到了96521个数据包，后面的因为缓冲区满的原因全部丢失。这里不会像TCP一样堆积数据包会粘包，UDP不会，而是会一次取一个，按顺序取。不同的设置的缓冲区大容量不同。

# 三、避免丢包

既然我们知道了丢包的原因，那么在好实际开发中我们应尽量避免丢包问题。

1、在接收端人为创建缓冲区，也即是说，如果一个数据包处理的时间很长，那么我们可以将接收和处理分开，将接收的数据存储到代码层面。

2、再遇见数据包很大时，可以采用分片多次传输，最后将数据在接收端汇总处理，避免数据堆积。

3、解决方案：接收处理分离

这里使用多进程来处理数据，与接收数据使用不同的线程，互不影响，这样不会导致数据包的接收速度，所以缓冲区不会堆积，避免数据包的丢失。手动创建了一个本地数据缓冲区，使用一个列表将接收的数据存储，使用多进程不断处理。这里相当于队列是一个本地缓冲区，可以避免数据丢包，但是需要注意的是本地缓冲区不能也不能超过大小。

**Client**

```python
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
            time.sleep(0.001)
            if i == 100000:
                break

if __name__ == "__main__":
    main()
```

**Server**

```python
from multiprocessing import Queue
import socket
import time
from  multiprocessing import Process

def task(data_list:Queue):
    '''模拟处理处理'''
    while True:
        data = data_list.get()
        time.sleep(10)
     
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
```

# 四、解决丢包

## 1、回复机制

**Server**

```python
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
```

**Client**

```python
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
```

这里通过回传机制确定数据正常到达，服务端接收到数据必须在指定时间内给予回复，否则默认数据包丢失，将上一次消息重发，这样可以解决数据丢包。（注意服务端必须给予回复，否则将会一直收到重复消息。）

## 2、奇偶检验

用于检测数据包是否错误，这里指的是数据包破损，导致数据包是不完整的，这时候使用回复机制无法找到错误，这里使用奇偶检验就可以解决这个问题。客户端除了在指定时间内需要接收数据外，还要根据回复的消息判断数据包是否破损。

**Server**

```python
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
```

**Client**

```python
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
```

## 3、前向纠错

这种情况比较复杂，是通过更复杂的编码方案规则，在数据中添加冗余数据用于数据纠错。根据自己定义的一套规则，将判断规则需要的数据，添加到数据包中，冗余数据用于来纠错。例如海明码（这里不做具体举例，因为比较复杂）

# 五、总结

UDP（用户数据报协议）是一种无连接的传输层协议，因其不保证数据包的顺序到达和不具备内置重传机制，导致在网络拥塞、接收缓冲区溢出或发送频率过快等情况下容易出现丢包现象。为应对这些问题，可以在应用层实现重传机制、使用前向纠错码等方法。这些方法在一定程度上可以缓解UDP通信中的丢包问题，提高数据传输的可靠性和效率。