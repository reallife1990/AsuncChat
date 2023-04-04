"""
5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

"""

import subprocess
import chardet


PING_1 = subprocess.Popen(['ping', 'yandex.ru'], stdout=subprocess.PIPE)
PING_2 = subprocess.Popen(['ping', 'youtube.com'], stdout=subprocess.PIPE)
target=[PING_1,PING_2]
for tar in target:
    for line in tar.stdout:
        result = chardet.detect(line)
        print(result)
        line = line.decode(result['encoding']).encode('utf-8')
        print(line.decode('utf-8'))
