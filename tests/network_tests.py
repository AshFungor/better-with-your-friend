from network_utils import Server, Client, HOST, PORT

import unittest
import logging
from unittest.mock import patch
from mockselector.selector import MockSocket, ListenSocket, MockSelector
from selectors import EVENT_READ, EVENT_WRITE


class NetworkTest(unittest.TestCase):

    def test_base_message_received(self):
        test_data = bytes()

        def send_data(_bytes):
            print(_bytes)

        test_sock = MockSocket()
        test_sock.send = send_data
        listen_test_sock = ListenSocket((test_sock,))
        listen_test_sock.setblocking = lambda state: state
        sel = MockSelector((listen_test_sock, (test_sock, EVENT_WRITE), (test_sock, EVENT_WRITE)))

        with patch('socket.socket', autospec=True) as socket:
            with patch('selectors.DefaultSelector', autospec=True) as selector:
                socket.return_value = listen_test_sock
                selector.return_value = sel

                server = Server(b'ab')
                server.loop()
                server.loop()

        print(test_data)
