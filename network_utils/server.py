import logging
import socket
import selectors
import types
import struct

hostname = socket.gethostname()

HOST = socket.gethostbyname(hostname)
PORT = 10000


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

    b_msg_len = 0
    c_msg_len = 8

    def __init__(self, init_byte_array = bytes()):
        global HOST, PORT
        logging.basicConfig(filename='server_log.txt', encoding='UTF-8', level=logging.DEBUG)

        self.__sel = selectors.DefaultSelector()
        self.__state = 0
        self.__init_byte_array = init_byte_array
        self.__connected = False

        self.__client_position = (0, 0)
        self.__host_position = (0, 0)

        init_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        init_sock.bind((HOST, PORT))
        init_sock.listen(1)
        init_sock.setblocking(False)

        self.__sel.register(init_sock, selectors.EVENT_READ)
        logging.debug(f"listening on {PORT}, host is {HOST}")

        self.__init_sock = init_sock
        logging.debug('server started')

    @property
    def connected(self):
        return self.__connected

    @property
    def client_position(self):
        return self.__client_position
    
    @property
    def host_position(self):
        return self.__host_position

    @host_position.setter
    def host_position(self, position):
        if isinstance(position, tuple) and len(position) == 2:
            self.__host_position = position
            return
        raise ValueError('position must be tuple of size 2')  

    def initialize_main_phase(self):
        if self.__state is not None:
            logging.debug('server state is on')
            self.__state = True
        else:
            logging.error('instance of server is inactive, refusing call')

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
        self.__connected = True
        self.__sel.register(connection, selectors.EVENT_WRITE | selectors.EVENT_READ, data=data)

    def __handle_connection(self, key, mask):
        sock = key.fileobj
        data = key.data

        if self.__state == 0:
            if self.__init_byte_array:
                data.bytes_send = self.__init_byte_array
                self.__init_byte_array = bytes()
            if mask & selectors.EVENT_WRITE:
                sent = sock.send(data.bytes_send)
                data.bytes_send = data.bytes_send[sent:]
                if not data.bytes_send:
                    logging.debug('initial message sent, switching server to -1')
                    self.__state = -1

        if self.__state == 1:

            if mask & selectors.EVENT_READ:
                received = sock.recv(Server.c_msg_len)
                if received:
                    if len(data.bytes_recv) + len(received) == Server.c_msg_len:
                        x, y = struct.unpack('2f', data.bytes_recv + received)
                        self.__client_position = (x, y)
                        data.bytes_recv = bytes()
                    else:
                        data.bytes_recv += received
                else:
                    logging.error(f'client {data.address} has ended connection')
                    raise Exception(f'client {data.address} has ended connection')

            if mask & selectors.EVENT_WRITE:
                if not data.bytes_send:
                    data.bytes_send = struct.pack('2f', *self.host_position)
                sent = sock.send(data.bytes_send)
                data.bytes_send = data.bytes_send[sent:]

    def loop(self):
        events = self.__sel.select()
        for key, mask in events:
            if not key.data:
                self.__accept_connection(key.fileobj)
            else:
                self.__handle_connection(key, mask)

    def close(self):
        self.__sel.close()
        self.__state = None
