import logging
import socket
import selectors
import types
import struct
from typing import Union

from .server import Server

"""
Файл с классом клиента для подключения
к хосту.
"""


# protocol scheme
# server     client
# listen
# ______ <- connect
# accept connection
# b_msg -> ______
# transfer complete
# wait for game start
# ______ -> game phase
# ______ <-> ______
# ** game phase **
# close connection on quit

class Client:
    """
    Класс для установки peer-to-peer соединения.
    """

    def __init__(self, host: str, port: int) -> 'Client':
        """
        Единственный конструктор принимает IP хоста и порт.

        Args:
            host (str): 4-х байтный IP адрес сервера
            port (int): целочисленное значение порта для подключения

        Returns:
            экземпляр класса Client
        """
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
            logging.error(f'could not connect to {host} on {port}')
            raise ConnectionError(f'could not connect to {host} on {port}')

        data = types.SimpleNamespace(
            bytes_recv=b'', bytes_send=b''
        )

        logging.debug('client is ready')
        self.__sel.register(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)
        self.__sock = sock

    # вспомогательный метод для установки соединения
    def __connect(self, sock: socket.socket) -> bool:
        try:
            sock.connect_ex((self.__host, self.__port))
        except:
            return False
        finally:
            return True

    @property
    def client_position(self) -> tuple[int, int]:
        """
        :obj:`tuple` of :obj:`int`: кортеж координат клиента,
        который должен обновляться каждый цикл.
        """
        return self.__client_position

    @client_position.setter
    def client_position(self, position: tuple[int, int]) -> None:
        if isinstance(position, tuple) and len(position) == 2:
            if isinstance(position[0], int) and isinstance(position[1], int):
                self.__client_position = position
                return
        raise ValueError('position must be tuple of size 2')

    @property
    def host_position(self) -> tuple[int, int]:
        """
         :obj:`tuple` of :obj:`int`: кортеж координат хоста,
         обновление которых происходит во время итераций.
        """
        return self.__host_position

    @property
    def state(self) -> int:
        """
        int: текущее состояние сервера, константы означают:
        0 -> получение базового сообщения,
        -1 -> получение базового сообщения завершено,
        ожидание сигнала от сервера,
        1 -> активная фаза обмена данных (координат).
        """
        return self.__state

    @property
    def base_message(self) -> Union[None, int, bytes]:
        """
        :obj:`int` or :obj:`None` or :obj:`bytes`:
        базовое сообщение клиента. `None` означает,
        что сообщение не существует, значение (-1) - еще
        не получено, объект `bytes` - само сообщение.
        """
        if self.__base_message is None:
            return
        if len(self.__base_message) < Server.b_msg_len:
            return -1
        return self.__base_message

    # вспомогательный метод для обработки сокета
    def __handle_connection(self, key: selectors.SelectorKey, mask: int) -> None:
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            if self.state == 0:
                recv_data = sock.recv(Server.b_msg_len)
                logging.debug(f'state: {self.__state}, bytes received: {recv_data}')
                if len(recv_data) + len(data.bytes_recv) == Server.b_msg_len:
                    self.__base_message = data.bytes_recv + recv_data
                    self.__state = -1
                    data.bytes_recv = bytes()
                else:
                    data.bytes_recv += recv_data
            elif abs(self.state) == 1:
                recv_data = sock.recv(Server.c_msg_len)
                logging.debug(f'state: {self.__state}, bytes received: {recv_data}')
                if len(recv_data) + len(data.bytes_recv) == Server.c_msg_len:
                    x, y = struct.unpack('2f', data.bytes_recv + recv_data)
                    self.__host_position = (x, y)
                    data.bytes_recv = bytes()
                else:
                    data.bytes_recv += recv_data
                self.__state = 1
        if mask & selectors.EVENT_WRITE:
            if self.state == 1:
                if not data.bytes_send:
                    data.bytes_send = struct.pack('2f', *self.client_position)
                sent = sock.send(data.bytes_send)
                logging.debug(f'bytes sent: {sent}')
                data.bytes_send = data.bytes_send[sent:]

    def loop(self, timeout=0) -> None:
        """
        Главный метод класса, отвечающий за
        обработку сообщений хоста и
        отправку данных клиентом.

        Args:
             timeout (int): время задержки в секундах
        """
        events = self.__sel.select(timeout)
        if events:
            for key, mask in events:
                self.__handle_connection(key, mask)

    def close(self) -> None:
        """
        Деструктор класса, который закрывает запись
        и чтение сокета.
        """
        logging.debug('closing instance, setting state to None')
        self.__sel.close()
        self.__state = None
