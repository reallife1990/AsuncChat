import json
import unittest
from utils.utils import check_params, send_message, get_message


class TestCheckParams(unittest.TestCase):

    def test_check_clients_data_actually(self):
        self.assertEqual(check_params(['-p','2222','-a','192.168.0.0'],True),('192.168.0.0', 2222,'OK'))

    def test_check_clients_default_ip(self):
        self.assertEqual(check_params(['-p', '2222'],True), ('127.0.0.1', 2222,'OK'))

    def test_check_clients_bad_ip(self):
        self.assertEqual(check_params(['-a', '222'], True)[2], '222 - недопустимый ip')

    def test_check_clients_bad_port(self):
        self.assertEqual(check_params(['-p', '222'], True)[2], 'недопустимый порт. диапозон 1024-65535')

    def test_check_clients_default_all(self):
        self.assertEqual(check_params([],True), ('127.0.0.1', 7777, "OK"))

    def test_check_server_data_actually(self):
        self.assertEqual(check_params(['-p','2222','-a','192.168.0.0']),('192.168.0.0', 2222,'OK'))

    def test_check_server_default_ip(self):
        self.assertEqual(check_params(['-p', '2222']), ('', 2222,'OK'))

    def test_check_server_bad_ip(self):
        self.assertEqual(check_params(['-a', '222'])[2], '222 - недопустимый ip')

    def test_check_server_bad_port(self):
        self.assertEqual(check_params(['-p', '222'])[2], 'недопустимый порт. диапозон 1024-65535')

    def test_check_server_default_all(self):
        self.assertEqual(check_params([]), ('', 7777, "OK"))


class TestSocket:
    '''
    Тестовый класс для тестирования отправки и получения,
    при создании требует словарь, который будет прогонятся
    через тестовую функцию
    '''
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.receved_message = None

    def send(self, message_to_send):
        """
        Тестовая функция отправки, корретно  кодирует сообщение,
        так-же сохраняет что должно было отправлено в сокет.
        message_to_send - то, что отправляем в сокет
        :param message_to_send:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        # кодирует сообщение
        self.encoded_message = json_test_message.encode('utf-8')
        # сохраняем что должно было отправлено в сокет
        self.receved_message = message_to_send

    def recv(self, max_len):
        """
        Получаем данные из сокета
        :param max_len:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode('utf-8')


class Tests(unittest.TestCase):
    '''
    Тестовый класс, собственно выполняющий тестирование.
    '''
    test_dict_send = {
        'action': 'presence',
        'time': 111111.111111,

    }
    test_dict_recv_ok = {'response': 200}
    test_dict_recv_err = {
        'response': 400,
        'error': 'Bad Request'
    }

    def test_send_message(self):

        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertEqual(test_socket.encoded_message, test_socket.receved_message)
        with self.assertRaises(Exception):
            send_message(test_socket, test_socket)

    def test_get_message(self):
        """
        Тест функции приёма сообщения
        :return:
        """
        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        test_sock_err = TestSocket(self.test_dict_recv_err)
        self.assertEqual(get_message(test_sock_ok), self.test_dict_recv_ok)
        self.assertEqual(get_message(test_sock_err), self.test_dict_recv_err)


if __name__ == '__main__':
    unittest.main()
