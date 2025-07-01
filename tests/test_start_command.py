import os
import pytest
from telethon import TelegramClient
from sqlalchemy import select
from data.db import AsyncSessionLocal
from data.models import User, Workout, Exercise
from .utils import check_answer


@pytest.mark.asyncio
async def test_new_user_registration(client: TelegramClient, db_session: AsyncSessionLocal):
    result = await db_session.execute(select(User))
    assert len(result.scalars().all()) == 0

    entity = await client.get_entity(os.getenv('BOT_USERNAME'))
    await client.send_message(entity, '/start')

    await check_answer(client, entity, 'Добро пожаловать в GymezyBot!')

    # Проверяем создание пользователя в базе данных
    result = await db_session.execute(select(User))
    users = result.scalars().all()
    assert len(users) == 1

    user = users[0]
    assert user.telegram_id == int(os.getenv('USER_ID'))
    assert user.username == os.getenv('USERNAME')


@pytest.mark.asyncio
async def test_existing_user_welcome(client: TelegramClient, db_session: AsyncSessionLocal):
    test_user = User(
        telegram_id=int(os.getenv('USER_ID')),
        username="test_user",
        name="Test"
    )
    db_session.add(test_user)
    await db_session.commit()

    entity = await client.get_entity(os.getenv('BOT_USERNAME'))
    await client.send_message(entity, '/start')

    await check_answer(client, entity, 'За сегодня тренировок нет')
    await check_answer(client, entity, 'С возвращением, Test', 2)


@pytest.mark.asyncio
async def test_existing_user_with_workouts_welcome(client: TelegramClient, db_session: AsyncSessionLocal):
    test_user = User(
        telegram_id=int(os.getenv('USER_ID')),
        username="test_user",
        name="Test"
    )
    test_exercise = Exercise(
        name='test ex',
        unit='count'
    )
    test_workout = Workout(
        user_id=1,
        exercise_id=1,
        value=15
    )
    db_session.add_all([test_user, test_exercise, test_workout])
    await db_session.commit()

    entity = await client.get_entity(os.getenv('BOT_USERNAME'))
    await client.send_message(entity, '/start')

    await check_answer(client, entity, 'С возвращением, Test', 2)
    await check_answer(client, entity, 'Ваши тренировки за сегодня:')
    await check_answer(client, entity, '1. Test ex 15 раз')
