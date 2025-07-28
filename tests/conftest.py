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
from bot.utils.bot import get_bot
from data.db import AsyncSessionLocal
from data.models import Base
from data.factories import UserFactory, ExerciseFactory


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
    await asyncio.sleep(1)
    yield
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass


@pytest.fixture
async def new_user():
    return await UserFactory.create_async()


@pytest.fixture()
async def user_with_workouts():
    async def _create(workouts_count=1):
        return await UserFactory.create_with_workouts(workouts_count=workouts_count)

    return _create


@pytest.fixture()
async def new_exercise():
    return await ExerciseFactory.create_async()


@pytest.fixture(autouse=True)
def _get_botname():
    return os.getenv('BOT_USERNAME')


@pytest.fixture(autouse=True)
async def conversation(client: TelegramClient, _get_botname):
    entity = await client.get_entity(_get_botname)
    async with client.conversation(entity, exclusive=False) as conv:
        yield conv
        try:
            await conv.cancel()
        except Exception:
            pass