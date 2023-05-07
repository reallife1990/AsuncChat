import subprocess


while True:
    try:
        txt = input('Выберите количество клиентов')
        num = int(txt)
        if num<1:
            raise AttributeError
        subprocess.Popen('python server.py',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE)
        for i in range(num):
            subprocess.Popen('python client.py',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE)
        break
    except ValueError:
        print(f'{txt} - не число')
    except AttributeError:
        print(f'Количество клиентом не может быть менее одного')
