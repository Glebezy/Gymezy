from aiogram import Bot, Dispatcher, types
import os
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
user = os.getenv("USER_ID")


async def test_bot():
    await bot.send_message(user, "Бот работает!")  # Замени 123456789 на свой ID

if __name__ == '__main__':
    import asyncio
    asyncio.run(test_bot())
