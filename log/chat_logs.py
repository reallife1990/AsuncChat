import os
import time

PATH_LOGS = os.path.join(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0], 'chat-logs')


def chat_logs_write(mes_type, name, text):
    date = time.strftime("%d.%m.%Y %H:%M", time.localtime())
    if mes_type == 'private':
        file = os.path.join(PATH_LOGS, f'{name}.txt')
    elif mes_type == 'message':
        file = os.path.join(PATH_LOGS, f'chat_log.txt')
    elif mes_type == 'exit':
        file = os.path.join(PATH_LOGS, f'chat_log.txt')
        name = 'server'
    else:
        return False
    # print(file)
    if os.path.isfile(file) is False:
        # print(file)
        f = open(file, 'w')
        f.close()
    write_log = open(file, 'a', encoding='UTF-8')
    write_log.write(f'{date} {name} {text}\n')
    write_log.close()
    # print(file)
    return True


# print(time.strftime("%d.%m.%Y %H:%M", time.localtime()) )
# private_log('message','jhg','123')