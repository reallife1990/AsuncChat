"""
4. Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

"""

VAR_1_STR = 'разработка'
VAR_2_STR = 'администрирование'
VAR_3_STR = 'protocol'
VAR_4_STR = 'standard'

STR_LIST = [VAR_1_STR, VAR_2_STR, VAR_3_STR, VAR_4_STR]


def coder(data_list, method):
    result=[]
    for el in data_list:
        if method == 'decode':
            result.append(el.decode('utf-8'))

        elif method == 'encode':
            result.append(el.encode('utf-8'))
        else:
            raise Exception(f'method "{method}" not supported')
    return result

enc_values=coder(STR_LIST,'encode')
print(enc_values)
print(coder(enc_values,'decode'))
