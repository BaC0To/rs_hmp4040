import socket
import time

TCP_IP = '192.168.1.10'
PORT = 5024
BUFFER_SIZE = 1024
MESSAGE = '*IDN?\n'
ADDRESS = (TCP_IP, PORT)

my_bytes = bytearray()

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(ADDRESS)
    my_bytes.extend(map(ord, MESSAGE))
    s.send(my_bytes)
    time.sleep(0.2)
    data_byte_str = s.recv(1024)
    data =  str(data_byte_str, encoding='utf-8')
    print((data))
    MESSAGE = 'SOURce:VOLTage?\n'
    my_bytes.extend(map(ord, MESSAGE))
    s.send(my_bytes)
    time.sleep(0.2)
    data_byte_str = s.recv(2048)
    data =  str(data_byte_str, encoding='utf-8')
    print((data))

    s.close()

except Exception as e:
    print(str(e))
    s.close()
