from ipaddress import ip_address
from subprocess import Popen, PIPE


ip_addresses = ['yandex.ru', '2.2.2.2', '8.8.8.8', '192.168.0.101']


def ping(list_ip_addresses, timeout=500, requests=1):
    for address in list_ip_addresses:
        try:
            address = ip_address(address)
        # обойдем такие исключения
        # ValueError: 'yandex.ru' does not appear to be an IPv4 or IPv6 address
        # хотя можно преобразовать доменное имя к ip-адресу
        except ValueError:
            pass
        proc = Popen(f"ping {address} -w {timeout} -n {requests}",  stdout=PIPE)
        proc.wait()
        # проверяем код завершения подпроцесса--=============================================================-------В

        if proc.returncode == 0:
            print(f'{address} - Узел доступен')
        else:
            print(f'{address} - Узел недоступен')


ping(ip_addresses)
