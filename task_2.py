"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""

from ipaddress import ip_address
from subprocess import Popen, PIPE


def ping(list_ip_addresses, timeout=500, requests=1):
    # results = {'Доступные узлы': "", 'Недоступные узлы': ""}  # словарь с результатами
    for address in list_ip_addresses:
        try:
            address = ip_address(address)
        except ValueError:
            pass
        proc = Popen(f"ping {address} -w {timeout} -n {requests}",  stdout=PIPE)
        proc.wait()
        # проверяем код завершения подпроцесса--=============================================================-------В

        if proc.returncode == 0:
            print(f'{address} - Узел доступен')
        else:
            print(f'{address} - Узел недоступен')


def host_range_ping():
    while True:
        # запрос первоначального адреса
        start_ip = input('Введите первоначальный адрес: ')
        try:

            data = list(start_ip.split('.'))
            if len(data) != 4:
                raise ValueError(f'{start_ip} - не является ip адресом')
            for num, el in enumerate(data):
                if not el.isnumeric() or int(el) < 0 or int(el) > 254:
                    raise ValueError(f'{start_ip} - не является ip адресом (min:0 max:254)')
            las_oct = int(start_ip.split('.')[3])
            break
        except Exception as e:
            print(e)
    while True:
        # запрос на количество проверяемых адресов
        end_ip = input('Сколько адресов проверить?: ')
        if not end_ip.isnumeric():
            print('Необходимо ввести число: ')
        else:
            # по условию меняется только последний октет
            if (las_oct+int(end_ip)) > 254:
                print(f"Можем менять только последний октет, т.е. "
                      f"максимальное число хостов для проверки: {254-las_oct}")
            else:
                break

    host_list = []
    # формируем список ip адресов
    [host_list.append(str(ip_address(start_ip)+x)) for x in range(int(end_ip))]
    return ping(host_list)


host_range_ping()


