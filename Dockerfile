FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем папки для данных и логов
RUN mkdir -p data logs

# Запускаем бота
CMD ["python", "run.py"]