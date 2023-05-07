import time
import argparse
from socket import *
from utils.utils import *
import log.server_log_config as logs
from log.info_log import log
import select


# класс-заготовка для сообщений в чате
class Message():
     __slots__ = ['action', 'user', 'time', 'text']

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

    #список клиентов
    writers = {}
    readers = {}

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
        print('проц зашёл')
        logs.server_logger.debug(f'Разбор сообщения от клиента : {message}')

        # Если это сообщение о подключении ридера,
        # отвечаем об успехе и пишем в чат о новом пользователе
        if message['action'] == 'start':
            code = client.getpeername()
            print(code)
            send_message(writers.get(code), {'response': 200})
            obj = Message()
            obj.action = 'enter'
            obj.user = message['user']
            obj.time = message['time']
            obj.text = message['message']
            messages_list.append(obj)
            return
        # # Если это сообщение, то добавляем его в очередь сообщений.
        elif message['action'] == 'message':
            obj = Message()
            obj.action = 'message'
            obj.user = message['user']
            obj.time = message['time']
            obj.text = message['message']
            messages_list.append(obj)
            return
        # # Если это сообщение о выходе, отправляем ридеру
        # команду на закрытие, сообщаем в чат, удаляем оба
        # соединения из словарей
        elif message['action'] == 'exit':
            code = client.getpeername()
            print(code)
            send_message(readers.get(code), {'action': 'quit'})
            readers.pop(code)
            writers.pop(code)
            logs.server_logger.debug(f'Клиент с кодом : {code} покинул чат')
            obj = Message()
            obj.action = 'exit'
            obj.user = message['user']
            obj.time = message['time']
            obj.text = message['message']
            messages_list.append(obj)
            return
        else:
            logs.server_logger.warning(f'Неизвестная команда: {message["action"]} от {client}')

        return


    # собираем пару писатель-слушатель (новые запросы)
    @log
    def create_full_client(client, addr):
        message = get_message(client)
        print(message)
        if message['action'] == 'connect':
            writers[addr[0], addr[1]] = client
            print(writers)
            send_message(client, {'response': 300})
            logs.server_logger.info(f'{addr} - отправитель')
        elif message['action'] == 'accept':
            tmp = (addr[0], int(message['write_port']))
            if tmp in writers.keys():
                print('add reader')
                readers[tmp] = client
                print(readers)
                logs.server_logger.info(f'{addr} - слушатель для {tmp}')
                # print(writers.get(tmp))
                send_message(writers.get(tmp), {'response': 201})


    # Основной цикл программы сервера
    while True:
        # Ждём подключения, если таймаут вышел, ловим исключение.
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            logs.server_logger.info(f'Установлено соедение с ПК {client_address}')
            create_full_client(client, client_address)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        # Проверяем на наличие ждущих клиенто
        #  проверка на готовую пару
        try:
            if len(list(writers.keys() & readers.keys())) > 0:
                recv_data_lst, send_data_lst, err_lst = select.select(writers.values(), readers.values(), [], 1)
                print(f' r{len(recv_data_lst)}, s{len(send_data_lst)}, e{len(err_lst)}')
        except OSError:
            pass

        # принимаем сообщения и если там есть сообщения,
        # кладём в словарь, если ошибка, исключаем клиента.
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    # (cообщение, список сообщений, клиент)
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message)
                except:
                    logs.server_logger.info(f' Ридер клиента {client_with_message.getpeername()} '
                                f'отключился от сервера.')

        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        if messages and send_data_lst:
            print(messages)
            print(messages[0].action, messages[0].user, messages[0].text)
            message = {
                'action': messages[0].action,
                'user': messages[0].user,
                'time': messages[0].time,
                'text': messages[0].text
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_message(waiting_client, message)
                except:
                    # если сообщение не доставлено отключаем оба клиента
                    logs.server_logger.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')

                    readers.pop(waiting_client.getpeername())
                    writers.pop(waiting_client.getpeername())


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
