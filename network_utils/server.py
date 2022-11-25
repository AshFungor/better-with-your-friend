import socket
import selectors
import types
import struct

hostname=socket.gethostname()
HOST=socket.gethostbyname(hostname)

CLIENTS = 0
MSGLEN = 8
# HOST = '127.0.0.1'
PORT = 10000
C1_RC = False
C2_RC = False

clients = {}
coordinates = {}
sel = selectors.DefaultSelector()

init_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
init_sock.bind((HOST, PORT))
init_sock.listen(2)

print(f'initializing server on {HOST}, listen port is {PORT}')

init_sock.setblocking(False)
sel.register(init_sock, selectors.EVENT_READ)

def checkout_client(address, status, set_other=0):
    global C1_RC, \
        C2_RC
    if clients[address] == set_other:
        C1_RC = status
    else:
        C2_RC = status

def get_status(address):
    global C1_RC, \
        C2_RC
    if clients[address] == 0:
        return C2_RC
    else:
        return C1_RC

def accept_connection(sock):
    global CLIENTS
    global init_sock, sel
    print('receiving new connection')
    if CLIENTS > 1:
        print(f'clients counter is {CLIENTS}, refusing connection')
        print(f'closing listening port')
        sel.unregister(init_sock)
        init_sock.close()
        return
    CLIENTS += 1
    connection, address = sock.accept()
    print(f'connection accepted to {address}')
    connection.setblocking(False)
    data = types.SimpleNamespace(
        address = address, bytes_send = b'', bytes_recv = b''
    )
    clients[address] = CLIENTS - 1
    coordinates[clients[address]] = []
    sel.register(connection, selectors.EVENT_WRITE | selectors.EVENT_READ, data=data)

def handle_connection(key, event):
    global MSGLEN, C1_RC, C2_RC
    sock = key.fileobj
    data = key.data
    client_number = clients[data.address]
    if event & selectors.EVENT_READ:
        if client_number == 0 and not C1_RC or client_number == 1 and not C2_RC:
            print(f'reading {data.address}')
            received = sock.recv(MSGLEN)
            if received:
                if len(data.bytes_recv) + len(received) == MSGLEN:
                    x, y = struct.unpack('2f', data.bytes_recv + received)
                    coordinates[client_number].append((x, y))
                    checkout_client(data.address, True)
                    print(f'cycle on {data.address} completed, read {MSGLEN} bytes, set RC status')
                else:
                    data.bytes_recv += received
            else:
                raise Exception(f"client {data.address} shut down")
    if event & selectors.EVENT_WRITE:
        if get_status(data.address):
            print(f'another client is ready, writing from {data.address}')
            if not data.bytes_send:
                another_c_number = 1 if client_number == 0 else 0
                data.bytes_send = struct.pack('2f', *coordinates[another_c_number].pop())
            sent = sock.send(data.bytes_send)
            data.bytes_send = data.bytes_send[sent:]
            if not data.bytes_send:
                print(f'cycle on {data.address} completed, wrote {MSGLEN} bytes')
                checkout_client(data.address, False, set_other=1)

try:

    while True:
        events = sel.select()
        for key, mask in events:
            if not key.data:
                accept_connection(key.fileobj)
            else:
                handle_connection(key, mask)

except KeyboardInterrupt:
    print(f'shutting down')

finally:
    sel.close()

         