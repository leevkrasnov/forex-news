import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

COUNTRY_FLAGS = {
    "США": "🇺🇸", "Еврозона": "🇪🇺", "Китай": "🇨🇳", "Япония": "🇯🇵",
    "Великобритания": "🇬🇧", "Канада": "🇨🇦", "Австралия": "🇦🇺", "Германия": "🇩🇪",
    "Франция": "🇫🇷", "Италия": "🇮🇹", "Швейцария": "🇨🇭", "Россия": "🇷🇺",
    "Индия": "🇮🇳", "Бразилия": "🇧🇷", "Южная Корея": "🇰🇷", "Новая Зеландия": "🇳🇿",
    "Испания": "🇪🇸"
}
DEFAULT_FLAG = "🌍"

def get_forex_news():
    url = "https://ru.investing.com/economic-calendar/"
    headers = {"User-Agent": "Mozilla/5.0"}
    for attempt in range(3):
        try:
            logger.info("Запрос к ru.investing.com...")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            news_list = []
            rows = soup.select('tr.js-event-item')

            logger.info(f"Найдено {len(rows)} строк событий")

            for row in rows:
                time = row.get('data-event-datetime', "")
                title = row.select_one('td.event').get_text(strip=True)
                country_element = row.select_one('td.flagCur span.ceFlags')
                country = country_element['title'] if country_element else ""
                stars = row.select('i.grayFullBullishIcon')

                fact_element = row.select_one('td.act')
                fact = fact_element.get_text(strip=True) if fact_element and fact_element.get_text(strip=True) else "n/a"
                forecast_element = row.select_one('td.fore')
                forecast = forecast_element.get_text(strip=True) if forecast_element and forecast_element.get_text(strip=True) else "n/a"
                previous_element = row.select_one('td.prev')
                previous = previous_element.get_text(strip=True) if previous_element and previous_element.get_text(strip=True) else "n/a"

                if len(stars) >= 2:
                    try:
                        formatted_time = datetime.strptime(time, '%Y/%m/%d %H:%M:%S').strftime('%H:%M')
                        logger.debug(f"Новость: {title}, время: {formatted_time}, страна: {country}")
                    except ValueError as e:
                        logger.warning(f"Ошибка формата времени для '{title}': {e}")
                        formatted_time = "Неизвестное время"

                    news_list.append({
                        'time': formatted_time,
                        'country': country,
                        'title': title,
                        'fact': fact,
                        'forecast': forecast,
                        'previous': previous,
                        'importance': len(stars)
                    })

            logger.info(f"Получено {len(news_list)} новостей с высокой значимостью")
            return news_list
        except RequestException as e:
            logger.error(f"Ошибка парсинга (попытка {attempt + 1}): {e}")
            if attempt < 2:
                logger.info("Повторная попытка через 5 секунд...")
                import time
                time.sleep(5)
            else:
                logger.error("Не удалось получить новости после 3 попыток")
                return []
        except Exception as e:
            logger.error(f"Непредвиденная ошибка: {e}")
            return []

def format_news(news):
    flag = COUNTRY_FLAGS.get(news['country'], DEFAULT_FLAG)
    importance = "⭐" * news['importance']
    return (
        f"🕰 <b>{news['time']}</b>    {importance}\n"
        f"{flag} <b>{news['country']}</b>\n"
        f"📋 <i>{news['title']}</i>\n"
        f"Факт: {news['fact']} | Прогноз: {news['forecast']} | Пред: {news['previous']}\n"
    )