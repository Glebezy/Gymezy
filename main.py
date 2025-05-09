import os
from dotenv import load_dotenv
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from bot.handlers.start import start_command

logging.basicConfig(level=logging.DEBUG)


load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
user = os.getenv("USER_ID")
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await start_command(message)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
