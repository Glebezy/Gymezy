import asyncio

import pytest
import pytest_asyncio
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
from app import start_bot
from bot.utils import get_bot
from data.db import AsyncSessionLocal
from data.models import Base


@pytest_asyncio.fixture(scope='session')
async def client() -> TelegramClient:
    client = TelegramClient(
        StringSession(os.getenv('SESSION_STRING')),
        os.getenv('API_ID'),
        os.getenv('API_HASH')
    )

    client.session.set_dc(2, '149.154.167.40', 80)

    await client.connect()

    try:
        yield client
    finally:
        await client.disconnect()


def _get_test_http_session():
    return AiohttpSession(
            api=TelegramAPIServer(
                base="https://api.telegram.org/bot{token}/test/{method}",
                file="https://api.telegram.org/file/bot{token}/test/{path}",
            )
        )


@pytest_asyncio.fixture()
async def db_session() -> AsyncSession:
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


@pytest_asyncio.fixture(autouse=True)
async def clean_db(db_session: AsyncSession):
    for table in reversed(Base.metadata.sorted_tables):
        await db_session.execute(table.delete())
    await db_session.commit()


@pytest.fixture(scope="session", autouse=True)
async def run_bot_in_background():
    bot_task = asyncio.create_task(start_bot('test', get_bot('test')))
    yield
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass
