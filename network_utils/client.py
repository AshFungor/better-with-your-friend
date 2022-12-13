import logging
import socket
import selectors
import types
import struct

from .server import Server

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

class Client:

    def __init__(self, host, port):
        logging.basicConfig(filename='client_log.txt', encoding='UTF-8', level=logging.DEBUG)

        self.__sel = selectors.DefaultSelector()
        self.__state = 0
        self.__host = host
        self.__port = port

        self.__client_position = (0, 0)
        self.__host_position = (0, 0)
        self.__base_message = bytes() if Server.b_msg_len > 0 else None

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        if not self.__connect(sock):
            raise Exception(f'could not connect to {host} on {port}')

        data = types.SimpleNamespace(
            bytes_recv=b'', bytes_send=b''
        )

        self.__sel.register(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)
        self.__sock = sock

    def __connect(self, sock):
        try:
            sock.connect_ex((self.__host, self.__port))
        except:
            return False
        finally:
            return True

    @property
    def client_position(self):
        return self.__client_position

    @client_position.setter
    def client_position(self, position):
        if isinstance(position, tuple) and len(position) == 2:
            self.__host_position = position
            return
        raise ValueError('position must be tuple of size 2')
    
    @property
    def host_position(self):
        return self.__host_position

    @property
    def state(self):
        return self.__state
    
    @property
    def base_message(self):
        if self.__base_message is None:
            return
        if len(self.__base_message) < Server.b_msg_len:
            return -1
        return self.__base_message

    def __handle_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            if self.state == 0:
                recv_data = sock.recv(Server.b_msg_len)
                if len(recv_data) + len(data.bytes_recv) == Server.b_msg_len:
                    self.__base_message = data.bytes_recv + recv_data
                    self.__state = -1
                    data.bytes_recv = bytes()
            if abs(self.state) == 1:
                recv_data = sock.recv(Server.c_msg_len)
                if len(recv_data) + len(data.bytes_recv) == Server.c_msg_len:
                    x, y = struct.unpack('2f', data.bytes_recv + recv_data)
                    self.__host_position = (x, y)
                    data.bytes_recv = bytes()
                else:
                    data.bytes_recv += recv_data
                self.__state = 1
        elif mask & selectors.EVENT_WRITE:
            if self.state == 1:
                if not data.bytes_send:
                    data.bytes_send = struct.pack('2f', *self.client_position)
                sent = sock.send(data.bytes_send)
                data.bytes_send = data.bytes_send[sent:]

    def loop(self, timeout=0):
        events = self.__sel.select(timeout)
        if events:
            for key, mask in events:
                self.__handle_connection(key, mask)
