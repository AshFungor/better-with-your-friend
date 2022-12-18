import logging
import selectors
import socket
import struct
import types

"""
Файл с классом хоста для подключения
к клиенту.

Attributes:
    HOST (str): текущий хост
    PORT (int): порт для прослушивания
"""

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5000


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
    """
    Класс для хоста peer-to-peer соединения

    Attributes:
        b_msg_len (int): длина базового сообщения
        c_msg_len (int): длина регулярного сообщения
    """

    b_msg_len = 0
    c_msg_len = 8

    def __init__(self, init_byte_array=bytes()) -> 'Server':
        """
        Единственный конструктор класса, принимающий, если нужно
        базовое сообщение.

        Args:
            init_byte_array (bytes): базовое сообщение

        Returns:
            экземпляр класса Server
        """
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
    def connected(self) -> bool:
        """
        bool: статус подключения клиента (подключен он или нет?)
        """
        return self.__connected

    @property
    def client_position(self) -> tuple[int, int]:
        """
        :obj:`tuple` of :obj:`int`: кортеж координат клиента,
        обновляемый с почти каждой итерацией
        """
        return self.__client_position

    @property
    def host_position(self) -> tuple[int, int]:
        """
        :obj:`tuple` of :obj:`int`: кортеж координат хоста,
        который должен обновляться каждый цикл.
        """
        return self.__host_position

    @host_position.setter
    def host_position(self, position: tuple[int, int]) -> None:
        if isinstance(position, tuple) and len(position) == 2:
            if isinstance(position[0], int) and isinstance(position[1], int):
                self.__host_position = position
                return
        raise ValueError('position must be tuple of size 2')

    def initialize_main_phase(self) -> None:
        """
        Метод для перевода хоста в активную фазу.
        """
        if self.__state is not None:
            logging.debug('server state is on')
            self.__state = True
        else:
            logging.error('instance of server is inactive, refusing call')
            raise Exception('instance of server is inactive, refusing call')

    # вспомогательный метод для настройки соединения
    def __accept_connection(self, sock: socket.socket) -> None:
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

    # вспомогательный метод для обработки сокета
    def __handle_connection(self, key: selectors.SelectorKey, mask: int) -> None:
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
                logging.debug(f'bytes received: {received}')
                if received:
                    if len(data.bytes_recv) + len(received) == Server.c_msg_len:
                        x, y = map(int, struct.unpack('2f', data.bytes_recv + received))
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
                logging.debug(f'bytes written: {sent}')
                data.bytes_send = data.bytes_send[sent:]

    def loop(self, timeout=0.01) -> None:
        """
        Главный метод класса, отвечающий за
        обработку сообщений клиента и
        отправку данных хостом.

        Args:
             timeout (int): время задержки в секундах
        """
        events = self.__sel.select(timeout)
        for key, mask in events:
            if not key.data:
                self.__accept_connection(key.fileobj)
            else:
                self.__handle_connection(key, mask)

    def close(self) -> None:
        """
        Деструктор класса, который закрывает запись
        и чтение сокета.
        """
        logging.debug('closing instance, setting state to None')
        self.__sel.close()
        self.__state = None
