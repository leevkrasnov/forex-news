import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramRetryAfter
from src.news_parser import get_forex_news, format_news
from src.ai_generator import generate_comment, generate_educational_tip
from datetime import datetime
import logging
from aiohttp import ClientConnectorError

logger = logging.getLogger(__name__)

# Словарь для русских месяцев
RUSSIAN_MONTHS = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

def setup_bot():
    from src.config import BOT_TOKEN, GROUP_ID
    if not BOT_TOKEN or not GROUP_ID:
        logger.error("BOT_TOKEN или GROUP_ID не установлены")
        raise ValueError("Необходимы BOT_TOKEN и GROUP_ID")
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    return bot, dp

async def split_message(full_text, max_length=4096):
    messages = []
    current_message = ""
    for line in full_text.split("\n"):
        if len(current_message) + len(line) + 1 <= max_length:
            current_message += line + "\n"
        else:
            messages.append(current_message.strip())
            current_message = line + "\n"
    if current_message.strip():
        messages.append(current_message.strip())
    return messages

async def send_news_to_telegram(bot: Bot):
    from src.config import GROUP_ID
    try:
        logger.info("Запуск отправки новостей")
        news_list = get_forex_news()
        if not news_list:
            for attempt in range(3):
                try:
                    await bot.send_message(chat_id=GROUP_ID, text="Новостей с высокой значимостью не найдено.", parse_mode='HTML')
                    logger.info("Новостей не найдено")
                    break
                except (ClientConnectorError, TelegramRetryAfter) as e:
                    logger.warning(f"Ошибка отправки (попытка {attempt + 1}): {e}")
                    await asyncio.sleep(5 if isinstance(e, ClientConnectorError) else e.retry_after)
            return

        # Форматирование даты на русском без локали
        today = datetime.now()
        day = today.day
        month = RUSSIAN_MONTHS[today.month]
        year = today.year
        current_date = f"{day} {month} {year}"
        full_text = f"<b>🔗 События и новости за {current_date}</b>\n\n"

        for news in news_list:
            formatted = format_news(news)
            comment = await generate_comment(news)
            tip = await generate_educational_tip(news)

            block = f"{formatted}\n💬 <i>{comment}</i>\n\n"
            if tip:
                block += f"📘 {tip}\n"
            block += "------------------------------\n\n"
            full_text += block

        messages = await split_message(full_text)
        for message in messages:
            for attempt in range(3):
                try:
                    await bot.send_message(chat_id=GROUP_ID, text=message, parse_mode='HTML')
                    await asyncio.sleep(1)
                    logger.info("Сообщение отправлено в Telegram")
                    break
                except TelegramRetryAfter as e:
                    logger.warning(f"Превышен лимит Telegram. Жду {e.retry_after} сек.")
                    await asyncio.sleep(e.retry_after)
                except ClientConnectorError as e:
                    logger.warning(f"Ошибка подключения (попытка {attempt + 1}): {e}")
                    await asyncio.sleep(5)
                    if attempt == 2:
                        logger.error("Не удалось отправить сообщение после 3 попыток")
    except Exception as e:
        logger.error(f"Ошибка при отправке новостей: {e}")

async def cmd_start(message: Message):
    await message.answer("Привет! Я помогу тебе с новостям по рынку Forex.")