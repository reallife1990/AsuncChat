import logging
import logging.handlers
import os

# формат записи
FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# определяем путь для файла логов
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

#хэндлер с параметрами для ведения логов
LOG_FILE = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf-8', interval=1, when='D')
LOG_FILE.setFormatter(FORMATTER)

#создаём логгер
server_logger = logging.getLogger('server')

#выбор уровня
server_logger.setLevel(logging.DEBUG)

#добавляем хэндлер с параметрами
server_logger.addHandler(LOG_FILE)