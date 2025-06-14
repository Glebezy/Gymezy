import os
from dotenv import load_dotenv
import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.handlers.exercise import router as exercise_router
from bot.handlers.workout import router as workout_router
from bot.handlers.stats import router as stats_router
from bot.handlers.start import router as start_router

from data.db import init_db

logging.basicConfig(level=logging.DEBUG)


load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
user = os.getenv("USER_ID")
dp = Dispatcher()
dp.include_routers(exercise_router, workout_router, stats_router, start_router)


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
