import time
from socket import *
import sys
from utils.utils import *


def create_message():
    message = {
        'action': 'presence',
        'time': time.time(),
        'user': 'test'
    }
    return message


def process_ans(message):

    if 'response' in message:
        if message['response'] == 200:
            return '200 : OK'
        return f'400 : {message["error"]}'
    raise ValueError


def work(params):
    print(f'работа по адресу: {params[0]}:{params[1]}')
    pipe = socket(AF_INET, SOCK_STREAM)
    for i in params:
        print(type(i))
    pipe.connect(params)
    message_to_server = create_message()
    send_message(pipe, message_to_server)
    try:
        answer = process_ans(get_message(pipe))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера.')
    print(params)


def start():
    """
    получение параметров
    :return:
    """

    if len(sys.argv)<2 or sys.argv[1] !='run':
        print('commands:\nrun -a ip address(default 127.0.0.1) -p port(default 7777)')
        sys.exit(0)
    else:
        params = sys.argv[2:]
        print(params)
        # checked_data = check.start(params)
        work(check_params(params, True))


if __name__ =='__main__':
    start()