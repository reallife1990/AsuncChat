import argparse
import time
from socket import *
from utils.utils import *
import log.client_log_config as logs
from log.info_log import log
import threading


def incoming_messages(pipe, a=False):
    cor_name = True
    while cor_name:
        try:
            message = get_message(pipe)
            logs.client_logger.debug(f' Получено сообщение {message}')
            # print(message)
            # если получено служебное сообщение
            if message.get('response'):
                if message['response'] == 300:
                    print('такое имя пользователя занято')
                    cor_name = False
                elif message['response'] == 200:
                    print('Добро пожаловать в чат')
            else:
                # обрабатываем сообщение
                print(f'\nСообщение от {message["user"]}: {message["text"]}')
        except:
            pass


def create_message(user, txt, act=None, from_user=None):
    """
    Конфигурирование сообщения
    :param user: имя пользователя
    :param txt: сообщение
    :param act: тип( подключение, сообщение. выход)
    :param from_user: для кого. None -  сообщение всем(не используется)
    :return: dict для отправки
    """
    message = {
        'action': 'message',
        'time': time.time(),
        'user': user,
        'message': txt,
        'from': from_user
    }

    if act is True:
        message['action'] = 'start'
    elif act is False:
        message['action'] = 'exit'
    # print(message)
    return message


def send_to_chat(pipe, user):
    while True:
        mes = input('сообщение:')
        to_user = input('кому:')
        if mes == '%%exit%%':
            send_message(pipe, create_message(user, '', False))
            print('вы вышли из чата')
            time.sleep(3)
            sys.exit(0)
        else:
            send_message(pipe,  create_message(user, mes, None, to_user))
            time.sleep(1)


@log
def work():
    ip, port, user = start()
    # print(f'работа по адресу: {params[0]}:{params[1]}')
    pipe = socket(AF_INET, SOCK_STREAM)

    try:
        pipe.connect((ip, port))
        print('соединение ...')
        send_message(pipe, create_message(user, '', True))

        reader = threading.Thread(target=incoming_messages, args=(pipe,True))
        reader.daemon = True
        reader.start()

        sendler = threading.Thread(target=send_to_chat, args=(pipe, user))
        sendler.daemon = True
        sendler.start()

        while True:
            time.sleep(1)
            if sendler.is_alive() and reader.is_alive():
                continue
            break

    except (ValueError, json.JSONDecodeError):
        logs.client_logger.critical(f'Не удалось декодировать сообщение сервера.')
        print('Не удалось декодировать сообщение сервера.')
    except ConnectionRefusedError:
        logs.client_logger.critical(f'Не удалось подключиться к серверу  {ip}:{port}, '
                               f'конечный компьютер отверг запрос на подключение.')
        print(f'Не удалось подключиться к серверу  {ip}:{port}, '
                               f'конечный компьютер отверг запрос на подключение.')






@log
def start():
    """
    получение параметров, имени пользователя
    :return:
    """
    logs.client_logger.info('начало')
    ip, port = get_params()
    print(ip, port)
    user = input('Введите имя в чате: ')
    while user.isspace() or len(user) < 1:
        print('Имя не может быть пустым!')
        user = input('Введите имя в чате: ')
    print('подключаемся....')
    return ip, port, user


def get_params():
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
        return (listen_address, listen_port)
    else:
        res = check_params(listen_address,listen_port)
        logs.client_logger.critical(res)
        print(res)
        sys.exit(1)



if __name__ =='__main__':
    work()
