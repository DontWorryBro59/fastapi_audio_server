# Используем официальный Python образ
FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем pyproject.toml и poetry.lock в контейнер
COPY pyproject.toml poetry.lock /app/

# Устанавливаем Poetry
RUN pip install --upgrade pip && pip install poetry

# Устанавливаем зависимости проекта
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Копируем весь проект в контейнер
COPY . /app/

# Открываем порт для работы приложения
EXPOSE 8000

# Устанавливаем переменную окружения для правильного импорта
ENV PYTHONPATH=/app

# Команда для запуска приложения
CMD ["python", "app/main.py"]