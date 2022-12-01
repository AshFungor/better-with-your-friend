import logging
import socket
import selectors
import types
import struct

hostname = socket.gethostname()

HOST = socket.gethostbyname(hostname)
PORT = 10000
C_MSG_LEN = 8
B_MSG_LEN = 20
HOST_POSITION = None
LISTENER_POSITION = None

# protocol scheme
# server     client
# listen
# ______ <- connect
# accept connection
# wait for game start
# ______ -> game phase
# ______ <-> ______
# ** game phase **
# close connection on quit

class Server:

    def __init__(self):
        logging.basicConfig(filename='netlog.txt', encoding='UTF-8', level=logging.DEBUG)

        self.__other_coordinates = []
        self.__self_coordinates = []
        self.__sel = selectors.DefaultSelector()
        self.__state = 0
        self.__init_byte_array = bytes()
        self.connected = False

        init_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        init_sock.bind((HOST, PORT))
        init_sock.listen(1)
        logging.debug(f"listening on {PORT}, host is {HOST}")

        self.__init_sock = init_sock
        logging.debug('server started')

    def state_checkout(self):
        logging.debug('server state is on')
        self.__state = True

    def init_data(self, byte_array):
        logging.debug(f'initial data is set, size is {len(byte_array)}')
        self.__init_byte_array = byte_array

    def __accept_connection(self, sock):
        if self.connected:
            logging.debug('connection refused')
            return

        connection, address = sock.accept()
        logging.debug(f'connection accepted to {address}')

        connection.setblocking(False)
        data = types.SimpleNamespace(
            address=address, bytes_send=b'', bytes_recv=b''
        )
        self.connected = True
        self.__sel.register(connection, selectors.EVENT_WRITE | selectors.EVENT_READ, data=data)

    def __handle_connection(self, key, mask):
        sock = key.fileobj
        data = key.data

        if self.__state is 0:
            if self.__init_byte_array:
                data.bytes_send = self.__init_byte_array
                self.__init_byte_array = bytes()
            elif mask & selectors.EVENT_WRITE:
                sent = sock.send(data.bytes_send)
                data.bytes_send = data.bytes_send[sent:]
                if not data.bytes_send:
                    logging.debug('initial message sent, switching server to -1')
                    self.__state = -1

        if self.__state is 1:

            if mask & selectors.EVENT_READ:
                received = sock.recv(C_MSG_LEN)
                if received:
                    if len(data.bytes_recv) + len(received) == MSG_LEN:
                        x, y = struct.unpack('2f', data.bytes_recv + received)
                        LISTENER_POSITION = (x, y)
                        data.bytes_recv = bytes()
                    else:
                        data.bytes_recv += received
                else:
                    logging.error(f'client {data.address} has ended connection')
                    raise Exception(f'client {data.address} has ended connection')

            if mask & selectors.EVENT_WRITE:
                if not data.bytes_send:
                    data.bytes_send = struct.pack('2f', *HOST_POSITION)
                sent = sock.send(data.bytes_send)
                data.bytes_send = data.bytes_send[sent:]

    def loop(self):
        events = self.__sel.select()
        for key, mask in events:
            if not key.data:
                self.__accept_connection(key.fileobj)
            else:
                self.__handle_connection(key, mask)

