import logging
import sys

def log(func_to_log):
    def change_logger():
        """
        ф-ция выбора логгера в зависимости от адресата вызова
        :return: логгер
        """
        if sys.argv[0].split('.')[0] == 'client':
            import log.client_log_config as c
            return c.client_logger
        else:
            import log.server_log_config as s
            return s.server_logger

    def wrapper(*args, **kwargs):
        """Обертка"""
        logger = change_logger()
        ret = func_to_log(*args, **kwargs)
        logger.debug(f'Была вызвана функция {func_to_log.__name__} c параметрами {args}, {kwargs}. '
                     f'Вызов из модуля {func_to_log.__module__}. ')
        return ret
    return wrapper


