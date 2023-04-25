import json
import sys


def check_params(data_lst,cli=False):
    """
     проверка параметров
     cli-true проверка от клиента, false от сервера
    :return:
    """
    port = 7777
    addr = ''
    status = 'OK'
    if cli is True:
        addr = '127.0.0.1'
    # print(data_lst)
    for i, v in enumerate(data_lst):
        # print(i)
        if v == '-p':
            port = data_lst[i+1]
            # i+=1
        elif v == '-a':
            addr = data_lst[i+1]
        # print(port, addr)
    try:
        if int(port) < 1024 or int(port) > 65535:
            raise ValueError
        else:
            port = int(port)
    except ValueError:
        status = f'Порт "{port}" не разрешён. диапозон 1024-65535'

    if cli is True or len(addr) > 0:
        try:
            check_ip = addr.split('.')
            if len(check_ip) < 4:
                raise ValueError
            for i in check_ip:
                if int(i) < 0 or int(i) > 255:
                    raise ValueError
        except ValueError:
            status = f' Недопустимый ip -" {addr} "'

    return addr, port, status


def get_message(client):
    '''
    Утилита приёма и декодирования сообщения
    принимает байты выдаёт словарь, если принято что-то другое отдаёт ошибку значения
    :param client:
    :return:
    '''

    encoded_response = client.recv(1024)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode('utf-8')
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_message(sock, message):
    '''
    Утилита кодирования и отправки сообщения
    принимает словарь и отправляет его
    :param sock:
    :param message:
    :return:
    '''

    js_message = json.dumps(message)
    encoded_message = js_message.encode('utf-8')
    sock.send(encoded_message)

