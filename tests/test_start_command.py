import pytest
from telethon import TelegramClient
from sqlalchemy import select
from bot.utils.messages import Messages
from bot.utils.commands import Commands
from bot.handlers.stats import compile_daily_stats
from data.db import AsyncSessionLocal
from data.models import User
from .utils import check_answer


@pytest.mark.asyncio
async def test_new_user_registration(client: TelegramClient, db_session: AsyncSessionLocal, get_botname):
    result = await db_session.execute(select(User))
    assert len(result.scalars().all()) == 0

    entity = await client.get_entity(get_botname)
    await client.send_message(entity, Commands.START)
    telegram_user = await client.get_me()

    await check_answer(client, entity, Messages.WELCOME_TEXT)

    result = await db_session.execute(select(User))
    db_user = result.scalars().one()

    assert db_user.telegram_id == telegram_user.id
    assert db_user.username == telegram_user.username


@pytest.mark.asyncio
async def test_existing_user_welcome(client: TelegramClient, new_user, get_botname):
    entity = await client.get_entity(get_botname)
    await client.send_message(entity, Commands.START)

    await check_answer(client, entity, Messages.STATS_EMPTY_DAILY_TEXT)
    await check_answer(client, entity, Messages.LOGIN_TEXT.format(user_name=new_user.name), 2)


@pytest.mark.asyncio
async def test_existing_user_with_workouts_welcome(client: TelegramClient, user_with_workouts, get_botname):
    user = await user_with_workouts(3)
    daily_workout_stats = await compile_daily_stats(user.telegram_id)

    entity = await client.get_entity(get_botname)
    await client.send_message(entity, Commands.START)

    await check_answer(client, entity, Messages.LOGIN_TEXT.format(user_name=user.name), 2)
    await check_answer(client, entity, Messages.STATS_DAILY_TEXT)

    for exercise in daily_workout_stats:
        await check_answer(client, entity, exercise)
