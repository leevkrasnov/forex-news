from aiogram import Bot
import asyncio

async def get_chat_id():
    bot = Bot(token="7939100771:AAHxCnwXO9vjhcILrIxODIYv5nkrYorgNFw")
    updates = await bot.get_updates()
    for update in updates:
        if update.message and update.message.chat.type in ["group", "supergroup"]:
            print(f"Chat ID: {update.message.chat.id}")
    await bot.session.close()

asyncio.run(get_chat_id())