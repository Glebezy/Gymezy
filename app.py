import os
import asyncio
import logging
from aiogram import Dispatcher
from bot.handlers import start, exercise, workout, stats
from bot.utils.bot import get_bot
from data.db import create_db

logging.basicConfig(level=logging.INFO)


dp = Dispatcher()
dp.include_routers(exercise.router, workout.router, stats.router, start.router)


async def start_bot(env, bot):
    await create_db(env)
    await dp.start_polling(bot)


if __name__ == "__main__":
    env = os.getenv("ENV")
    asyncio.run(start_bot(env, get_bot(env)))
