import time
from socket import *
import sys
from utils.utils import *


def parse_message(message):
    '''
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента

    :param message:
    :return:
    '''
    if 'action' in message and message['action'] == 'presence' and 'time' in message:
        return {'response': 200}
    return {
        'response': 400,
        'error': 'Bad Request'
    }


def work(params):
    """
    работа с проверенными параметрами для сервера в цикле
    :param params: set(ip, port)
    :return:
    """
    print(f'слушаем : {params[0]}:{params[1]}')
    pipe = socket(AF_INET, SOCK_STREAM)
    pipe.bind(params)
    pipe.listen(5)

    while True:
        client, client_address = pipe.accept()
        try:
            incoming_message = get_message(client)
            print(incoming_message)
            response = parse_message(incoming_message)
            send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Принято некорретное сообщение от клиента.')
            client.close()


def start():
    """
    получение параметров
    :return:
    """

    if len(sys.argv) < 2 or sys.argv[1] != 'run':
        print('commands:\nrun -p port(default 7777) -a ip address(default listen all)')
        sys.exit(0)
    else:
        params = sys.argv[2:]
        print(params)
        # checked_data = check.start(params)
        work(check_params(params))


if __name__ == '__main__':
    start()
