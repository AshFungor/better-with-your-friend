from network_utils import Server, Client, HOST, PORT

import unittest
from unittest.mock import patch, Mock
import struct
from mockselector.selector import MockSocket, ListenSocket, MockSelector
from selectors import EVENT_READ, EVENT_WRITE


@patch('socket.socket')
@patch('selectors.DefaultSelector')
class ServerTests(unittest.TestCase):

    def setUp(self):
        self.test_sock = MockSocket()
        self.test_sock.send = Mock()
        self.test_sock.recv = Mock()
        self.listen_test_sock = ListenSocket([self.test_sock])
        self.listen_test_sock.setblocking = self.test_sock.setblocking = lambda el: el

    def test_base_message_received(self, selector, sock):
        test_data = b'gigachad'

        Server.b_msg_len = 16
        self.test_sock.send.return_value = Server.b_msg_len
        sel = MockSelector((self.listen_test_sock, (self.test_sock, EVENT_WRITE)))
        selector.return_value = sel
        sock.return_value = self.listen_test_sock
        server = Server(test_data)
        server.loop()
        server.loop()
        server.close()

        self.test_sock.send.assert_called_with(test_data)

    def test_active_phase(self, selector, sock):
        self.test_sock.send.return_value = Server.c_msg_len
        sel = MockSelector((self.listen_test_sock,
                            (self.test_sock, EVENT_WRITE | EVENT_READ),
                            (self.test_sock, EVENT_READ),
                            (self.test_sock, EVENT_WRITE)))

        selector.return_value = sel
        sock.return_value = self.listen_test_sock

        server = Server()
        server.loop()
        server.initialize_main_phase()
        # loop 1
        self.test_sock.recv.return_value = struct.pack('2f', 12, 12)
        server.host_position = (1, 2)
        server.loop()
        self.assertEqual(server.client_position, (12, 12))
        self.test_sock.send.assert_called_with(struct.pack('2f', 1, 2))
        # loop 2
        self.test_sock.recv.return_value = struct.pack('2f', 12, 0)
        server.loop()
        self.assertEqual(server.client_position, (12, 0))
        # loop 3
        server.host_position = (2, 3)
        server.loop()
        self.test_sock.send.assert_called_with(struct.pack('2f', 2, 3))
        server.close()

    def test_switcher_method(self, selector, sock):

        server = Server()
        server.__state = None
        self.assertRaises(Exception, server.initialize_main_phase())
        server.close()

    def test_position_setter(self, selector, sock):

        server = Server()
        with self.assertRaises(ValueError):
            server.host_position = 'hello world!'
        with self.assertRaises(ValueError):
            server.host_position = (1, 1, 1, 1)
        with self.assertRaises(ValueError):
            server.host_position = ('hello', ' world!')
        server.close()


@patch('socket.socket')
@patch('selectors.DefaultSelector')
class ClientTests(unittest.TestCase):

    def setUp(self):
        self.test_sock = MockSocket()
        self.test_sock.send = Mock()
        self.test_sock.recv = Mock()
        self.test_sock.setblocking = lambda el: el

    def test_base_message_transfer(self, selector, sock):
        test_data = bytes('gigachad', 'utf-8')
        Server.b_msg_len = len(test_data)
        sel = MockSelector(([(self.test_sock, EVENT_READ) for _ in range(len(test_data))]))
        selector.return_value = sel
        sock.return_value = self.test_sock
        client = Client(HOST, PORT)
        for i in range(len(test_data[:-1])):
            self.test_sock.recv.return_value = test_data[i:i + 1]
            client.loop()
            self.assertEqual(client.base_message, -1)

        self.test_sock.recv.return_value = test_data[len(test_data) - 1:len(test_data)]
        client.loop()
        self.assertEqual(client.base_message, test_data)
        client.close()

    def test_game_phase(self, selector, sock):
        self.test_sock.send.return_value = Server.c_msg_len
        sel = MockSelector(((self.test_sock, EVENT_READ),
                            (self.test_sock, EVENT_READ),
                            (self.test_sock, EVENT_WRITE | EVENT_READ),
                            (self.test_sock, EVENT_WRITE)))

        selector.return_value = sel
        sock.return_value = self.test_sock

        Server.b_msg_len = 0
        client = Client(HOST, PORT)
        self.test_sock.recv.return_value = bytes()
        client.loop()
        self.assertEqual(client.state, -1)
        # loop 1
        self.test_sock.recv.return_value = struct.pack('2f', -12, 0)
        client.loop()
        self.assertEqual(client.host_position, (-12, 0))
        self.assertEqual(client.state, 1)
        # loop 2
        self.test_sock.recv.return_value = struct.pack('2f', -12, -12)
        client.client_position = (-1, -2)
        client.loop()
        self.assertEqual(client.host_position, (-12, -12))
        self.test_sock.send.assert_called_with(struct.pack('2f', -1, -2))
        # loop 3
        client.client_position = (-2, -3)
        client.loop()
        self.test_sock.send.assert_called_with(struct.pack('2f', -2, -3))
        client.close()






