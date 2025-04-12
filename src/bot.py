from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramRetryAfter
from src.news_parser import get_forex_news, format_news
from src.ai_generator import generate_comment, generate_educational_tip
from datetime import datetime
import locale
import logging
import asyncio

logger = logging.getLogger(__name__)

# Устанавливаем локаль для русского языка
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # Для Windows: 'Russian_Russia.1251'

def setup_bot():
    from src.config import BOT_TOKEN, GROUP_ID
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
        news_list = get_forex_news()
        if not news_list:
            await bot.send_message(chat_id=GROUP_ID, text="Новостей с высокой значимостью не найдено.", parse_mode='HTML')
            logger.info("Новостей не найдено")
            return

        current_date = datetime.now().strftime('%d %B %Y')
        full_text = f"<b>🔗 Экономические новости за {current_date}</b>\n\n"

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
            try:
                await bot.send_message(chat_id=GROUP_ID, text=message, parse_mode='HTML')
                await asyncio.sleep(1)
                logger.info("Сообщение отправлено в Telegram")
            except TelegramRetryAfter as e:
                logger.warning(f"Превышен лимит Telegram. Жду {e.retry_after} сек.")
                await asyncio.sleep(e.retry_after)
                await bot.send_message(chat_id=GROUP_ID, text=message, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Ошибка при отправке новостей: {e}")

# Обработчик команды /start
async def cmd_start(message: Message):
    await message.answer("Привет! Я помогу тебе с новостями по рынку Forex.")