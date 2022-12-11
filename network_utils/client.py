import logging
import socket
import selectors
import types
import struct

from .server import B_MSG_LEN, C_MSG_LEN
from .server import CLIENT_POSITION, HOST_POSITION

B_MESSAGE = None


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

    def get_state(self):
        return self.__state

    def __handle_connection(self, key, mask):
        global B_MSG_LEN, C_MSG_LEN, B_MESSAGE, HOST_POSITION, CLIENT_POSITION
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            if self.__state == 0:
                recv_data = sock.recv(B_MSG_LEN)
                if len(recv_data) + len(data.bytes_recv) == B_MSG_LEN:
                    B_MESSAGE = data.bytes_recv + recv_data
                    self.__state = -1
                    data.bytes_recv = bytes()
            if self.__state == -1 or self.__state == 1:
                recv_data = sock.recv(C_MSG_LEN)
                if len(recv_data) + len(data.bytes_recv) == C_MSG_LEN:
                    x, y = struct.unpack('2f', data.bytes_recv + recv_data)
                    HOST_POSITION = (x, y)
                    data.bytes_recv = bytes()
                else:
                    data.bytes_recv += recv_data
                self.__state = 1
        elif mask & selectors.EVENT_WRITE:
            if self.__state == 1:
                if not data.bytes_send:
                    data.bytes_send = struct.pack('2f', *CLIENT_POSITION)
                sent = sock.send(data.bytes_send)
                data.bytes_send = data.bytes_send[sent:]

    def loop(self, timeout=0):
        events = self.__sel.select(timeout)
        if events:
            for key, mask in events:
                self.__handle_connection(key, mask)
