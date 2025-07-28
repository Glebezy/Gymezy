import allure
import pytest
from telethon import TelegramClient
from sqlalchemy import select
from bot.utils.messages import Messages
from bot.utils.commands import Commands
from bot.handlers.stats import compile_daily_stats
from data.db import AsyncSessionLocal
from data.models import User
from .utils import check_response, send_message


@allure.story('Start Commands')
@pytest.mark.asyncio
class TestStartCommand:

    @allure.title("Создание нового пользователя")
    async def test_new_user_registration(self, client: TelegramClient, db_session: AsyncSessionLocal, conversation):
        with allure.step('Проверяем пустую таблицу пользователей'):
            result = await db_session.execute(select(User))
            assert len(result.scalars().all()) == 0

        async with conversation as conv:
            await send_message(conv, Commands.START)
            await check_response(conv, Messages.WELCOME_TEXT)

        telegram_user = await client.get_me()

        with allure.step('Проверяем добавление пользователя в базу'):
            result = await db_session.execute(select(User))
            db_user = result.scalars().one()

            assert db_user.telegram_id == telegram_user.id
            assert db_user.username == telegram_user.username

    @allure.title("Приветствие существующего пользователя")
    async def test_existing_user_welcome(self, client: TelegramClient, new_user, conversation):
        async with conversation as conv:
            await send_message(conv, Commands.START)
            await check_response(conv, Messages.LOGIN_TEXT.format(user_name=new_user.name))
            await check_response(conv, Messages.STATS_EMPTY_DAILY_TEXT)

    @allure.title("Отображение дневной статистики существующего пользователя")
    async def test_existing_user_with_workouts_welcome(self, client: TelegramClient, user_with_workouts, conversation):
        user = await user_with_workouts(3)
        daily_workout_stats = await compile_daily_stats(user.telegram_id)

        async with conversation as conv:
            await send_message(conv, Commands.START)
            await check_response(conv, "\n".join(daily_workout_stats), count=2)
