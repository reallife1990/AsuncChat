import socket
import time
import argparse
import logging
import threading
import log.client_log_config as logs
from log.info_log import log
from utils.utils import *
from metaclasses import ClientMaker

# Инициализация клиентского логера
logger = logging.getLogger('client')


# Класс формировки и отправки сообщений на сервер и взаимодействия с пользователем.
class ClientSender(threading.Thread, metaclass=ClientMaker):
    def __init__(self, user, sock):
        self.user = user
        self.sock = sock

        super().__init__()

    def run(self):
        while True:
            # print('coobwenie', end='')
            mes = input()
            to_user = input('(оставьте пустым если сообщение для всех)\nкому:')
            if mes == '%%exit%%':
                send_message(self.sock, self.create_message(self.user, '', False))
                print('вы вышли из чата')
                time.sleep(3)
                sys.exit(0)
            else:
                send_message(self.sock, self.create_message(self.user, mes, None, to_user))
                time.sleep(1)
                print('\b' * 15, end='')
                print(f'Сообщение: ', end='')

    def create_message(self, user, txt, act=None, from_user=None):
        """
        Конфигурирование сообщения
        :param user: имя пользователя
        :param txt: сообщение
        :param act: тип( подключение, сообщение. выход)
        :param from_user: для кого.
        :return: dict для отправки
        """
        message = {
            'action': '',
            'time': time.time(),
            'user': user,
            'message': txt,
            'from': from_user
        }

        if act is True:
            message['action'] = 'start'
        elif act is False:
            message['action'] = 'exit'
        else:
            if from_user == '':
                message['action'] = 'message'
            else:
                message['action'] = 'private'
        return message


# Класс-приёмник сообщений с сервера. Принимает сообщения, выводит в консоль.
class ClientReader(threading.Thread, metaclass=ClientMaker):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def run(self):
        cor_name = True
        while cor_name:
            try:
                message = get_message(self.sock)
                logs.client_logger.debug(f' Получено сообщение {message}')
                # print(message)
                # если получено служебное сообщение
                if message.get('response'):
                    if message['response'] == 300:
                        print('такое имя пользователя занято')
                        cor_name = False
                    elif message['response'] == 200:
                        print('Добро пожаловать в чат')
                        print(f'\nСообщение: ', end='')
                else:
                    print('\b' * 15, end='')
                    # обрабатываем сообщение
                    print(f'{time.strftime("%H:%M", time.localtime(message["time"]))} [', end='')
                    if message['action'] == 'private':
                        print(f'Личное сообщение от ', end='')
                    print(f'{message["user"]}]: {message["text"]}', end='')
                    print(f'\nСообщение: ', end='')
            except:
                pass


@log
def presence_message(user):
    """
    Конфигурирование стартового сообщения
    :param user: имя пользователя
    :return: dict для отправки
    """
    message = {
        'action': 'start',
        'time': time.time(),
        'user': user,
        'message': '',
        'from': ''
    }
    return message

# Парсер аргументов коммандной строки
@log
def arg_parser():

    """
    Проверка входных параметров
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=7777, type=int, nargs='?')
    parser.add_argument('-a', default='127.0.0.1', type=str, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if check_params(listen_address, listen_port, True) == 'OK':
        logs.client_logger.debug(f'приняты данные ip:{listen_address},порт:{listen_port}')
        # work((listen_address, listen_port))

        logs.client_logger.info('запрос имени')

        user = input('Введите имя в чате: ')
        while user.isspace() or len(user) < 1:
            print('Имя не может быть пустым!')
            user = input('Введите имя в чате: ')
        print('подключаемся....')
        return listen_address, listen_port, user

    else:
        res = check_params(listen_address, listen_port)
        logs.client_logger.critical(res)
        print(res)
        sys.exit(1)


def main():
    # Сообщаем о запуске
    print('Консольный месседжер. Клиентский модуль.')

    # Загружаем параметы коммандной строки и имя пользователя
    server_address, server_port, user = arg_parser()

    logger.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address} , порт: {server_port}, имя пользователя: {user}')

    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, presence_message(user))
        # Если соединение с сервером установлено корректно, запускаем клиенский процесс приёма сообщний
        module_reciver = ClientReader(user, transport)
        module_reciver.daemon = True
        module_reciver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        module_sender = ClientSender(user, transport)
        module_sender.daemon = True
        module_sender.start()
        logger.debug('Запущены процессы')

        # Watchdog основной цикл, если один из потоков завершён, то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках, достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if module_reciver.is_alive() and module_sender.is_alive():
                continue
            break

    except (ValueError, json.JSONDecodeError):
        logs.client_logger.critical(f'Не удалось декодировать сообщение сервера.')
        print('Не удалось декодировать сообщение сервера.')
    except ConnectionRefusedError:
        logs.client_logger.critical(f'Не удалось подключиться к серверу  {server_address}:{server_port}, '
                               f'конечный компьютер отверг запрос на подключение.')
        print(f'Не удалось подключиться к серверу  {server_address}:{server_port}, '
                               f'конечный компьютер отверг запрос на подключение.')


if __name__ == '__main__':
    main()
