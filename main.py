import asyncio
import logging
import os
from src.bot import setup_bot
from src.scheduler import start_scheduler
from aiohttp import ClientConnectorError

# Создаём папку logs, если она не существует
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "bot.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Запуск бота...")
    bot, dp = setup_bot()
    while True:
        try:
            await asyncio.gather(start_scheduler(bot), dp.start_polling(bot))
            break
        except ClientConnectorError as e:
            logger.error(f"Ошибка подключения: {e}. Повторная попытка через 30 секунд...")
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            logger.info("Бот остановлен")
            break
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")