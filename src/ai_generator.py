from openai import AsyncOpenAI
from src.config import DEEPSEEK_API_KEY
import logging

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://hubai.loe.gg"
)

async def generate_comment(news):
    prompt = (
        f"Ты опытный трейдер на рынке Forex. Проанализируй новость и дай емкий, объективный анализ (разговорным языком). "
        f"Ответ должен быть сплошным текстом с абзацами, без смайликов, до 300 символов. "
        f"Следуй шаблону: Краткий анализ новости (1-2 предложения), Рекомендация к торговле (1 предложение), "
        f"Мнение (1 предложение, если умещается). Завершай мысль полностью, не обрывай предложения.\n\n"
        f"{news['time']} {news['country']}\n{news['title']}\n"
        f"Факт: {news['fact']} | Прогноз: {news['forecast']} | Пред: {news['previous']}"
    )
    for attempt in range(3):
        try:
            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Ты профессиональный трейдер Forex. Пиши кратко, точно, по делу."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=180
            )
            comment = response.choices[0].message.content.strip()
            if len(comment) > 300:
                comment = comment[:300].rsplit('.', 1)[0] + '.'
            logger.info("Комментарий успешно сгенерирован")
            return comment
        except Exception as e:
            logger.warning(f"Ошибка при генерации комментария (попытка {attempt + 1}): {e}")
            if attempt == 2:
                logger.error("Не удалось сгенерировать комментарий после 3 попыток")
                return "⚠️ Комментарий недоступен."
            await asyncio.sleep(2)

async def generate_educational_tip(news):
    prompt = (
        f"Дай краткий обучающий материал, связанный с этой новостью, который поможет начинающему трейдеру лучше понять ее влияние на экономику. "
        f"Если нет дельных советов, просто пропусти. Максимум 200 символов, но можно немного превысить при необходимости. "
        f"Не используй смайлики. Ответ должен быть сплошным текстом с соблюдением абзацев.\n\n"
        f"{news['time']} {news['country']}\n"
        f"{news['title']}\n"
        f"Факт: {news['fact']} | Прогноз: {news['forecast']} | Пред: {news['previous']}"
    )
    for attempt in range(3):
        try:
            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Ты обучающий ассистент для трейдеров. Пиши кратко, понятно."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=120
            )
            result = response.choices[0].message.content.strip()
            logger.info("Совет успешно сгенерирован")
            return result if result.lower() != "skip" else ""
        except Exception as e:
            logger.warning(f"Ошибка при генерации совета (попытка {attempt + 1}): {e}")
            if attempt == 2:
                logger.error("Не удалось сгенерировать совет после 3 попыток")
                return ""
            await asyncio.sleep(2)