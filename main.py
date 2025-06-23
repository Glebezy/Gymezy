import os
from dotenv import load_dotenv
import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.handlers import stats, start, workout, exercise
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
from data.db import init_db

logging.basicConfig(level=logging.DEBUG)

env = os.getenv('ENV', 'prod')  # По умолчанию 'test'
load_dotenv(f'.env.{env}')


def get_session():
    if os.getenv("env") == 'test':
        return AiohttpSession(
            api=TelegramAPIServer(
                base="https://api.telegram.org/bot{token}/test/{method}",
                file="https://api.telegram.org/file/bot{token}/test/{path}",
            )
        )
    else:
        return AiohttpSession()


bot = Bot(token=os.getenv("BOT_TOKEN"), session=get_session())
user = os.getenv("USER_ID")
dp = Dispatcher()
dp.include_routers(exercise.router, workout.router, stats.router, start.router)


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
