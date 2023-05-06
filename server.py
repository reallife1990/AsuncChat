import time
import argparse
from socket import *
from utils.utils import *
import log.server_log_config as logs
from log.info_log import log
import select


# класс-заготовка для сообщений в чате
class Message():
     __slots__ = ['action', 'user', 'time', 'text', 'to_user']


def main(listen_address, listen_port):
    """Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию"""

    logs.server_logger.info(
        f'Запущен сервер, порт для подключений: {listen_port}, '
        f'адрес с которого принимаются подключения: {listen_address}. '
        f'Если адрес не указан, принимаются соединения с любых адресов.')

    # Готовим сокет
    transport = socket(AF_INET, SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    # очередь сообщений
    messages = []

    #словарь клиентов имя:сокет
    clients = {}

    # Слушаем порт
    transport.listen(10)

    def process_client_message(message, messages_list, client):
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

        # Если это сообщение о подключении ридера,
        # отвечаем об успехе автору,
        # готовим приветственное сообщение( пока не используется)
        if message['action'] == 'start':
            time.sleep(1)
            print(message['user'])
            if message['user'] in clients.keys():
                send_message(client, {'response': 300})
            else:
                send_message(client, {'response': 200})

                obj = Message()
                obj.action = 'enter'
                obj.user = message['user']
                obj.time = message['time']
                obj.text = message['message']
                obj.to_user = message['from']
                clients[obj.user] = client
                messages_list.append(obj)
            return

        # # Если это сообщение, то добавляем его в очередь сообщений.
        elif message['action'] == 'message':
            obj = Message()
            obj.action = 'message'
            obj.user = message['user']
            obj.time = message['time']
            obj.text = message['message']
            obj.to_user = message['from']
            messages_list.append(obj)
            return
        # # Если это сообщение о выходе, готовим сообщение
        # в чат( не используется), удалаляем из словаря клиента,
        # пишем в логи о выходе
        elif message['action'] == 'exit':
            obj = Message()
            obj.action = 'exit'
            obj.user = message['user']
            obj.time = message['time']
            obj.text = message['message']
            obj.to_user = message['from']
            messages_list.append(obj)
            clients.pop(obj.user)
            logs.server_logger.debug(f'Клиент {client} покинул чат( по команде пользователя)')
            return
        else:
            logs.server_logger.warning(f'Неизвестная команда: {message["action"]} от {client}')

        return


    # Основной цикл программы сервера
    while True:
        # Ждём подключения, если таймаут вышел, ловим исключение.
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            logs.server_logger.info(f'Установлено соедение с ПК {client_address}')
            process_client_message(get_message(client), messages, client)


        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        # Принимаем клиентов

        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients.values(), clients.values(), [], 1)
                print(f' r{len(recv_data_lst)}, s{len(send_data_lst)}, e{len(err_lst)}')
        except OSError:
            pass

        # принимаем сообщения и если там есть сообщения,
        # кладём в словарь, если ошибка, исключаем клиента.
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    # print(get_message(client_with_message))
                    # (cообщение, список сообщений, клиент)
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message)
                except:
                    logs.server_logger.info(f' Ридер клиента {client_with_message.getpeername()} '
                                f'отключился от сервера.')

        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        if messages and send_data_lst:
            if messages[0].to_user and messages[0].to_user in clients.keys():
                print(messages)
                print(messages[0].action, messages[0].user, messages[0].text, messages[0].to_user)
                message = {
                    'action': messages[0].action,
                    'user': messages[0].user,
                    'time': messages[0].time,
                    'text': messages[0].text
                }
                try:
                    send_message(clients.get(messages[0].to_user), message)
                except:
                    # если не получилось доставить сообщение:
                    # пишем в логи, отписываем автору что пользователь вышел
                    logs.server_logger.info(f' клиент {messages[0].to_user} '
                                            f'отключился от сервера.')
                    clients.pop(messages[0].to_user)
                    message = {
                        'action': messages[0].action,
                        'user': 'server',
                        'time': messages[0].time,
                        'text': f'Пользователь {messages[0].to_user} - вышел'
                    }
                    send_message(clients.get(messages[0].user), message)
            elif messages[0].action =='message':
                message = {
                    'action': messages[0].action,
                    'user': 'server',
                    'time': messages[0].time,
                    'text': f'{messages[0].to_user} - такого пользователя нету'
                }
                send_message(clients.get(messages[0].user), message)
            del messages[0]


def get_params():
    """
    Обработка входящих параметров для запуска
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=7777, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if check_params(listen_address, listen_port) == 'OK':
        logs.server_logger.debug(f'приняты данные ip:{listen_address},порт:{listen_port}')
        # work((listen_address, listen_port))
        main(listen_address, listen_port)
    else:
        res = check_params(listen_address,listen_port)
        logs.server_logger.critical(res)
        print(res)
        sys.exit(1)

if __name__ == '__main__':
    get_params()
