
import socket
import selectors
import types
import struct
import time

sel = selectors.DefaultSelector()
HOST = '127.0.0.1'
PORT = 10000
MSGLEN = 8
S1_RC = True
S2_RC = True
COUNT = 0

sock_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('connected 1')
sock_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_1.setblocking(False)
sock_2.setblocking(False)
sock_1.connect_ex((HOST, PORT))
sock_2.connect_ex((HOST, PORT))

data1 = types.SimpleNamespace(
    coordinates = (12, 12), bytes_send = b'', bytes_recv = b'', num = 1
)
data2 = types.SimpleNamespace(
    coordinates = (-12, -12), bytes_send = b'', bytes_recv = b'', num = 2
)

sel.register(sock_1, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data1)
sel.register(sock_2, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data2)

def checkout_client(address, status, set_other=1):
    global S1_RC, \
        S2_RC
    if address == set_other:
        S1_RC = status
    else:
        S2_RC = status

def service_connection(key, mask):
    global MSGLEN, S1_RC, S2_RC, COUNT
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        if not S1_RC and data.num == 1 or not S2_RC and data.num == 2:
            recv_data = sock.recv(MSGLEN)  # Should be ready to read
            if len(recv_data) + len(data.bytes_recv) == MSGLEN:
                x, y = struct.unpack('2f', recv_data + data.bytes_recv)
                print(f'coords received: {x} and {y}')
                checkout_client(data.num, True)
                data.coordinates = (x + 1, y + 1)
                COUNT += 1
            else:
                data.recv_data += recv_data
    if mask & selectors.EVENT_WRITE:
        if S1_RC and data.num == 1 or S2_RC and data.num == 2:
            if not data.bytes_send:
                data.bytes_send = struct.pack('2f', *data.coordinates)
            sent = sock.send(data.bytes_send)
            data.bytes_send = data.bytes_send[sent:]
            if not data.bytes_send:
                print(f'cycle completed, wrote {MSGLEN} bytes')
                checkout_client(data.num, False)
                COUNT += 1

start = time.time()
try:
    while True:
        # time.sleep(2)
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        if time.time() - start > 1:
            raise KeyboardInterrupt('times up')

except KeyboardInterrupt:
    print('exiting')
finally:
    sock_1.close()
    sock_2.close()
    print(COUNT)