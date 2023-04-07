"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;
"""


import re
import csv

FILES_NAMES = ['info_1.txt', 'info_2.txt', 'info_3.txt']
PARAMS_DATA = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']


def get_data():
    """
    Parsing incoming files from 'FILES_NAMES' for PARAMS_DATA
    :return: parsed data from files (type:list)
    """
    data_lst = [PARAMS_DATA]
    for i in FILES_NAMES:
        data_file = []
        with open(i, 'r') as file:
            context = file.read()
            for param in PARAMS_DATA:
                find_data = re.compile(r'{}:\s*\S*'.format(param))
                data_file.append(find_data.findall(context)[0].split(':')[1].lstrip())
        data_lst.append(data_file)
    return data_lst


def create_csv_file(file_name):
    """
    Create report file
    :param file_name: name file for report
    :return: None
    """
    main_data = get_data()
    with open(file_name, 'w', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
        for row in main_data:
            writer.writerow(row)


create_csv_file('data_report.csv')



