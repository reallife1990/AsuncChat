import logging
import os

# формат записи
FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# определяем путь для файла логов
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')

#хэндлер с параметрами для ведения логов
LOG_FILE = logging.FileHandler(PATH, encoding='utf-8')
LOG_FILE.setFormatter(FORMATTER)

#создаём логгер
client_logger = logging.getLogger('client')

#выбор уровня
client_logger.setLevel(logging.DEBUG)

#добавляем хэндлер с параметрами
client_logger.addHandler(LOG_FILE)
