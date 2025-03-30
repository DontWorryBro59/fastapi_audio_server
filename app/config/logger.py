from loguru import logger
import sys
import os

# Создаём папку для логов, если её нет
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Полный путь до файла логов
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Удаляем стандартный обработчик
logger.remove()

# Логирование в консоль
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="INFO")

# Логирование в файл с ротацией и сжатием старых логов
logger.add(
    LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="5 days",
    compression="zip",
    encoding="utf-8"
)

def get_logger():
    return logger