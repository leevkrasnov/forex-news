import os
from dotenv import load_dotenv

load_dotenv()

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SEND_TIME = "16:40"
TIMEZONE = "Asia/Yekaterinburg"

# Проверка переменных окружения
if not all([BOT_TOKEN, GROUP_ID, DEEPSEEK_API_KEY]):
    raise ValueError("Не указаны все переменные окружения (BOT_TOKEN, GROUP_ID, DEEPSEEK_API_KEY)")