import os
from pathlib import Path

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from dotenv import load_dotenv


def _get_env(env: str):
    data_dir = Path(__file__).parent.parent
    load_dotenv(f'{data_dir}/.env.{env}')


def _get_http_session():
    if os.getenv("ENV") == 'test':
        return AiohttpSession(
            api=TelegramAPIServer(
                base="https://api.telegram.org/bot{token}/test/{method}",
                file="https://api.telegram.org/file/bot{token}/test/{path}",
            )
        )
    else:
        return AiohttpSession()


def get_bot(env: str = os.getenv('ENV')):
    _get_env(env)
    return Bot(token=os.getenv("BOT_TOKEN"), session=_get_http_session())
