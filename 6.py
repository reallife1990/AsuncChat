"""
6. Создать текстовый файл test_file.txt, заполнить его тремя строками:
«сетевое программирование», «сокет», «декоратор».
Проверить кодировку файла по умолчанию.
Принудительно открыть файл в формате Unicode и вывести его содержимое.
"""

from chardet.universaldetector import UniversalDetector

LINES_LST = ['сетевое программирование', 'сокет', 'декоратор']
with open('test.txt', 'w') as file:
    for line in LINES_LST:
        file.write(f'{line}\n')
file.close()

try:
    print('попытка открыть в utf-8:')
    with open('test.txt', 'r', encoding='utf-8') as file:
        CONTENT1 = file.read()
    print('успешно:')
    print(CONTENT1)
except UnicodeDecodeError as exc:
    print(f'Ошибка:\n{exc}')
    DETECTOR = UniversalDetector()
    with open('test.txt', 'rb') as test_file:
        for i in test_file:
            DETECTOR.feed(i)
            if DETECTOR.done:
                break
        DETECTOR.close()
    print(f'кодировка файла:{DETECTOR.result["encoding"]}')


    with open('test.txt', 'r', encoding=DETECTOR.result['encoding']) as file:
        CONTENT = file.read()
    print(CONTENT)
