import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SEND_TIME = os.getenv("SEND_TIME")
TIMEZONE = os.getenv("TIMEZONE")

# Проверка переменных окружения
missing_vars = []
if not BOT_TOKEN:
    missing_vars.append("BOT_TOKEN")
if not GROUP_ID:
    missing_vars.append("GROUP_ID")
else:
    # Проверка формата GROUP_ID
    try:
        if GROUP_ID.startswith("@"):
            logger.error("GROUP_ID должен быть числовым (например, -123456789), а не @username")
            missing_vars.append("GROUP_ID (некорректный формат)")
        else:
            int(GROUP_ID)
    except ValueError:
        logger.error("GROUP_ID должен быть числом")
        missing_vars.append("GROUP_ID (некорректный формат)")
if not DEEPSEEK_API_KEY:
    missing_vars.append("DEEPSEEK_API_KEY")

if missing_vars:
    logger.error(f"Не указаны переменные окружения: {', '.join(missing_vars)}")
    raise ValueError(f"Не указаны переменные окружения: {', '.join(missing_vars)}")