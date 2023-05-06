import argparse
import subprocess
import time
from socket import *
from utils.utils import *
import log.client_log_config as logs
from log.info_log import log


def start_reader(ip, port, writer_port):
    subprocess.Popen(f'python client_reader.py -a {ip} -p {port} -wp {writer_port}',
                                    creationflags=subprocess.CREATE_NEW_CONSOLE)


def create_message(user, txt, act=None):
    """
    Конфигурирование сообщения
    :param user: имя пользователя
    :param txt: сообщение
    :param act: тип( подключение, сообщение. выход)
    :return: dict для отправки
    """
    message = {
        'action': 'message',
        'time': time.time(),
        'user': user,
        'message': txt
    }
    if act is True:
        message['action'] = 'start'
    elif act is False:
        message['action'] = 'exit'
    # print(message)
    return message


def process_ans(message):
    if 'response' in message:
        if message['response'] == 300:
            return {"code": 300, 'text':'подключение к чату. 2 из 3 ОК'}
        elif message['response'] == 201:
            return {"code": 201, 'text':'ридер подлючился. 3 из 3 ОК'}
        elif message['response'] == 200:
            return {"code": 200, 'text':'всё готово'}
        return f'400 : {message["error"]}'
    raise ValueError

@log
def work():
    ip, port, user = start()
    #print(f'работа по адресу: {params[0]}:{params[1]}')
    pipe = socket(AF_INET, SOCK_STREAM)

    try:
        pipe.connect((ip, port))
        print('соединение 1 из 3 ОК')
        writer_port = pipe.getsockname()[1]
        # print(writer_port)
        send_message(pipe, {'action':'connect'})
        # send_message(pipe, create_message(user, '', True))
        start_reader(ip, port, writer_port)
        answer = process_ans(get_message(pipe))

        # процесс проверки всех необходимых подключений
        if answer['code'] == 300:
            print(answer['text'])
            answer2 = process_ans(get_message(pipe))
            # print(answer2)
            if answer2['code'] == 201:
                print(answer2['text'])
                send_message(pipe, create_message(user, '', True))
                answer3 = process_ans(get_message(pipe))
                # print(answer3)
                if answer3['code'] == 200:
                    print(answer3['text'])

        while True:
            mes = input('сообщение:')
            if mes == '%%exit%%':
                send_message(pipe, create_message(user, '', False))
                print('вы вышли из чата')
                time.sleep(3)
                sys.exit(0)
            else:
                send_message(pipe,  create_message(user, mes))

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
