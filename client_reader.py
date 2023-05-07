import argparse
import sys
import time
from socket import *
from utils.utils import *


def process_ans(message):
    chat = ''
    if 'action' in message:
        if 'time' in message:
            chat += f"{time.strftime('%H:%M',time.localtime(message['time']))} "
        else:
            if message['action'] == 'quit':
                print('вы вышли из чата')
                time.sleep(2)
                sys.exit(0)

        if message['action'] == 'enter':
            chat += f"{message['user']} вошёл в чат"
        elif message['action'] == 'exit':
            chat += f"{message['user']} покинул чат"
        elif message['action'] == 'message':
            chat += f"[ {message['user']} ]: {message['text']}"

    return chat




    # if 'response' in message:
    #     if message['response'] == 200:
    #         return '200 : OK'
    #     return f'400 : {message["error"]}'
    # raise ValueError


# получение сообщений
def incoming_chat(pipe):
    while True:
        # answer = process_ans(get_message(pipe))
        print(process_ans(get_message(pipe)))


def start_connect(ip, port, wp):
    """
    ф-ция для установления пары читатель-писатель
    :param ip:
    :param port:
    :param wp: порт клиента
    :return:
    """
    pipe = socket(AF_INET, SOCK_STREAM)
    pipe.connect((ip, port))
    send_message(pipe, {'action': "accept",
                        'write_port': wp
                        })
    incoming_chat(pipe)

def begin():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', type=str, default=2, help='ip for read chat')
    parser.add_argument('-p', type=int, default=7777, help='port for read chat')
    parser.add_argument('-wp', type=int, help='port for write chat')
    my_namespace = parser.parse_args()
    ip = my_namespace.a
    port = my_namespace.p
    wp = my_namespace.wp
    print('Подключаемся к серверу')
    time.sleep(1)
    start_connect(ip, port, wp)

begin()
