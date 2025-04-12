# src/scheduler.py
import schedule
import asyncio
import pytz
import logging
from src.bot import send_news_to_telegram
from src.config import SEND_TIME, TIMEZONE

logger = logging.getLogger(__name__)

def job(bot):
    logger.info("Запуск запланированной отправки новостей")
    loop = asyncio.get_event_loop()
    loop.create_task(send_news_to_telegram(bot))

async def start_scheduler(bot):
    schedule.every().day.at(SEND_TIME, tz=pytz.timezone(TIMEZONE)).do(job, bot=bot)
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)