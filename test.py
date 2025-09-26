from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv('TELEGRAM_BOT_TOKEN')
print(f"Длина токена: {len(token)}")
print(f"Первые 10 символов: {token[:10]}")
print(f"Токен: {token}")