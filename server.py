import socket
import argparse
import logging
import select
import time
import log.server_log_config as logs
from log.info_log import log
from utils.utils import *
from descripts import Port
from metaclasses import ServerMaker

# Инициализация логирования сервера.
logger = logging.getLogger('server')


class Message():
    __slots__ = ['action', 'user', 'time_at', 'text', 'to_user']

    def __init__(self, action, user, time_at, text, to_user):
        self.action = action
        self.user = user
        self.time_at = time_at
        self.text = text
        self.to_user = to_user

    def answ(self):
        "формирование ответа"
        return {'action': self.action,
                'user': self.user,
                'time': self.time_at,
                'text': self.text,
                'to_user': self.to_user}

    def answ_serv(self):
        "формирование ответа от сервера"
        mes = {'action': self.action,
                'user': 'server',
                'time': self.time_at,
                # 'text':  f'Пользователь {self.to_user} - вышел',
                'to_user': self.to_user
                }
        if self.action == 'enter':
            mes['text'] = f'{self.user} зашёл в чат'
        elif self.action == 'exit':
            mes['text'] = f'{self.user} покинул чат'
        else:
            mes['text'] = f'{self.to_user} - такого пользователя нету'
        return mes

# Парсер аргументов коммандной строки  и получения имени юзера.
@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=7777, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if check_params(listen_address, listen_port) == 'OK':
        logs.server_logger.debug(f'приняты данные ip:{listen_address},порт:{listen_port}')
        # work((listen_address, listen_port))
        return listen_address, listen_port
    else:
        res = check_params(listen_address, listen_port)
        logs.server_logger.critical(res)
        print(res)
        sys.exit(1)


# Основной класс сервера
class Server(metaclass=ServerMaker):
    port = Port()

    def __init__(self, listen_address, listen_port):
        # Параментры подключения
        self.addr = listen_address
        self.port = listen_port

        # Список подключённых клиентов.
        # self.clients = []

        # Список сообщений на отправку.
        self.messages = []

        # Словарь содержащий сопоставленные имена и соответствующие им сокеты.
        self.clients = dict()

        self.recive_lst = []
        self.send_lst = []
        self.err_lst = []

    def init_socket(self):
        logger.info(
            f'Запущен сервер, порт для подключений: {self.port} , адрес с которого принимаются подключения: {self.addr}. Если адрес не указан, принимаются соединения с любых адресов.')
        # Готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        # Начинаем слушать сокет.
        self.sock = transport
        self.sock.listen(10)

    def process_client_message(self, message, messages_list, client):
        """
        Обработчик сообщений от клиентов, принимает словарь - сообщение от клинта,
        проверяет корректность, пополняет список сообщений.
        :param message: декодированный словарь
        :param messages_list:список сообщений на отправку
        :param client: клиент
        :return:
        """
        print('сообщение пришло')
        logs.server_logger.debug(f'Разбор сообщения от клиента : {message}')
        print(message['action'])
        # Если это сообщение о подключении ридера,
        # отвечаем об успехе автору,
        # готовим приветственное сообщение( пока не используется)
        if message['action'] == 'start':
            time.sleep(1)
            print(f" вход {message['user']}")
            if message['user'] in self.clients.keys():
                send_message(client, {'response': 300})
            else:
                send_message(client, {'response': 200})
                obj = Message('enter', message['user'], message['time'], message['message'],message['from'])
                self.clients[obj.user] = client
                messages_list.append(obj)
            return

            # # Если это сообщение о выходе, готовим сообщение
            # в чат( не используется), удалаляем из словаря клиента,
            # пишем в логи о выходе
        elif message['action'] == 'exit':
            print('команда выход')
            obj = Message('exit', message['user'], message['time'], message['message'], message['from'])
            messages_list.append(obj)
            self.clients.pop(obj.user)
            logs.server_logger.debug(f'Клиент {client} покинул чат( по команде пользователя)')
            return


        # # Если это сообщение, то добавляем его в очередь сообщений.
        elif message['action'] == 'message' or 'private':
            print('сообщение')
            obj = Message(message['action'],message['user'], message['time'],message['message'],message['from'])

            messages_list.append(obj)
            print(message['from'])
            return
        else:
            logs.server_logger.warning(f'Неизвестная команда: {message["action"]} от {client}')

        return

    # def send_private_message(self):
    #     print(s)

    def main_loop(self):
        # Инициализация Сокета
        self.init_socket()
            # Основной цикл программы сервера

        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logs.server_logger.info(f'Установлено соедение с ПК {client_address}')
                self.process_client_message(get_message(client), self.messages, client)

            # Принимаем клиентов
            try:
                if self.clients:
                    self.recive_lst, self.send_lst, self.err_lst = select.select(self.clients.values(), self.clients.values(), [], 1)
                    print(f' r{len(self.recive_lst)}, s{len(self.send_lst)}, e{len(self.err_lst)}')
            except OSError:
                pass

            # принимаем сообщения и если там есть сообщения,
            # кладём в словарь, если ошибка, исключаем клиента.
            if self.recive_lst:
                for client_with_message in self.recive_lst:
                    try:
                        # print(get_message(client_with_message))
                        # (cообщение, список сообщений, клиент)
                        self.process_client_message(get_message(client_with_message),
                                               self.messages, client_with_message)
                    except:
                        logs.server_logger.info(f' Клиент {client_with_message.getpeername()} '
                                                f'отключился от сервера.')
                        self.recive_lst.remove(client_with_message)

            # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
            if self.messages and self.send_lst:
                print('есть сообщения и кому отправлять')
                print(self.messages[0].action)
                if self.messages[0].action == 'private':
                    if self.messages[0].to_user and self.messages[0].to_user in self.clients.keys():
                        print('приват с адресатом')
                        message = self.messages[0].answ()
                        try:
                            send_message(self.clients.get(self.messages[0].to_user),self.messages[0].answ())
                        except:
                            # если не получилось доставить сообщение:
                            # пишем в логи, отписываем автору что пользователь вышел
                            logs.server_logger.info(f' клиент {self.messages[0].to_user} '
                                                    f'отключился от сервера.')
                            self.clients.pop(self.messages[0].to_user)
                            # message = self.messages[0].answ_ser()
                            send_message(self.clients.get(self.messages[0].user), self.messages[0].answ_serv())
                    else:
                        # message = self.messages[0].answ_serv()
                        send_message(self.clients.get(self.messages[0].user), self.messages[0].answ_serv())
                elif self.messages[0].action =='message':
                    print('всем')
                    message = self.messages[0].answ()
                    try:
                        for client_with_mess in self.send_lst:
                            # (клиент, сообщение)
                            send_message(client_with_mess, self.messages[0].answ())
                    except:
                        logs.server_logger.info(f' клиент {self.messages[0].to_user} '
                                                f'отключился от сервера.')
                        self.clients.pop(self.messages[0].to_user)
                elif self.messages[0].action in ['enter', 'exit']:
                    message = self.messages[0].answ_serv()
                    try:
                        for client_with_mess in self.send_lst:
                            # (клиент, сообщение)
                            send_message(client_with_mess, self.messages[0].answ_serv())
                    except:
                        logs.server_logger.info(f' клиент {self.messages[0].to_user} '
                                                f'отключился от сервера.')
                        self.clients.pop(self.messages[0].to_user)

                else:
                    print('упс')
                    logs.server_logger.info(f' неизвестная команда {self.messages[0].action} '
                                            )
                del self.messages[0]


def main():
    # Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    listen_address, listen_port = arg_parser()

    # Создание экземпляра класса - сервера.
    server = Server(listen_address, listen_port)
    server.main_loop()


if __name__ == '__main__':
    main()
