from network_utils import Server, Client, HOST, PORT

import unittest
from unittest.mock import patch, Mock
import struct
from mockselector.selector import MockSocket, ListenSocket, MockSelector
from selectors import EVENT_READ, EVENT_WRITE


class NetworkTest(unittest.TestCase):

    @patch('socket.socket')
    @patch('selectors.DefaultSelector')
    def test_base_message_received(self, selector, sock):

        test_data = b'gigachad'

        Server.b_msg_len = 16
        test_sock = MockSocket()
        test_sock.send = Mock()
        test_sock.send.return_value = Server.b_msg_len
        listen_test_sock = ListenSocket([test_sock])
        listen_test_sock.setblocking = test_sock.setblocking = lambda el: el
        sel = MockSelector((listen_test_sock, (test_sock, EVENT_WRITE)))

        sock.return_value = listen_test_sock
        selector.return_value = sel

        server = Server(test_data)
        server.loop()
        server.loop()
        server.close()

        test_sock.send.assert_called_with(test_data)

    @patch('socket.socket')
    @patch('selectors.DefaultSelector')
    def test_active_phase(self, selector, sock):

        test_sock = MockSocket()
        test_sock.send = Mock()
        test_sock.recv = Mock()
        test_sock.send.return_value = Server.c_msg_len
        listen_test_sock = ListenSocket([test_sock])
        listen_test_sock.setblocking = test_sock.setblocking = lambda el: el
        sel = MockSelector((listen_test_sock,
                            (test_sock, EVENT_WRITE | EVENT_READ),
                            (test_sock, EVENT_READ),
                            (test_sock, EVENT_WRITE)))

        sock.return_value = listen_test_sock
        selector.return_value = sel

        server = Server()
        server.loop()
        server.initialize_main_phase()
        # loop 1
        test_sock.recv.return_value = b'\x00\x00@A\x00\x00@A'
        server.host_position = (1, 2)
        server.loop()
        self.assertEqual(server.client_position, (12, 12))
        test_sock.send.assert_called_with(struct.pack('2f', 1, 2))
        # loop 2
        test_sock.recv.return_value = b'\x00\x00@A\x00\x00\x00\x00'
        server.loop()
        self.assertEqual(server.client_position, (12, 0))
        # loop 3
        server.host_position = (2, 3)
        server.loop()
        test_sock.send.assert_called_with(struct.pack('2f', 2, 3))
        server.close()

