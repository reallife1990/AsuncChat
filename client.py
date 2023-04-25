import time
from socket import *
from utils.utils import *
import log.client_log_config as logs
from log.info_log import log

#client_logger = logging.getLogger('client')



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

@log
def work(params):
    #print(f'работа по адресу: {params[0]}:{params[1]}')
    pipe = socket(AF_INET, SOCK_STREAM)
    for i in params:
        print(type(i))
    try:
        pipe.connect(params)
        message_to_server = create_message()
        send_message(pipe, message_to_server)
        answer = process_ans(get_message(pipe))
        logs.client_logger.debug(f'Ответ сервера:{answer}')
        print(answer)
    except (ValueError, json.JSONDecodeError):
        logs.client_logger.critical(f'Не удалось декодировать сообщение сервера.')
        #print('Не удалось декодировать сообщение сервера.')
    except ConnectionRefusedError:
        logs.client_logger.critical(f'Не удалось подключиться к серверу  {params[0]}:{params[1]}, '
                               f'конечный компьютер отверг запрос на подключение.')
    print(params)

@log
def start():
    """
    получение параметров
    :return:
    """
    logs.client_logger.critical('ok')
    # print(log8())
    if len(sys.argv) < 2 or sys.argv[1] != 'run':
        logs.client_logger.critical(f'Ошибка! Запуск без команды run')
        print('commands:\nrun -a ip address(default 127.0.0.1) -p port(default 7777)')
        sys.exit(0)
    else:
        params = sys.argv[2:]
        print(params)
        # checked_data = check.start(params)
        result = (check_params(params, True))
        if result[2] == 'OK':
            logs.client_logger.debug(f'приняты данные ip:{result[0]},порт:{result[1]}')
            #print(result)
            work(result[:2])


        else:
            logs.client_logger.critical(f'Ошибка! {result[2]}')
            #print(result[2])
            sys.exit(0)


if __name__ =='__main__':
    start()