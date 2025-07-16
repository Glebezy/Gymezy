import pytest
from allure import step, title, story
from sqlalchemy import select

from bot.utils.commands import Commands
from bot.utils.messages import Messages
from data.models import Exercise
from utils import send_message, check_response, click_button

approve_buttons = [{
            "text": 'Подтвердить',
            "data": b'approve'
        }, {
            "text": 'Отмена',
            "data": b'cancel'
        }]


@story('Exercise Commands')
@pytest.mark.asyncio
class TestExerciseCommand:

    @pytest.mark.parametrize('exercise, unit', [("Упражнение1", "подходы")])
    @title("Добавление нового упражнения")
    async def test_new_exercise_added(self, client, db_session, conversation, exercise, unit):
        with step('Проверяем пустую таблицу упражнений'):
            result = await db_session.execute(select(Exercise))
            assert len(result.scalars().all()) == 0

        async with conversation as conv:
            await send_message(conv, Commands.ADD_EXERCISE)
            await check_response(conv, Messages.EXERCISE_NAME_REQUEST)
            await send_message(conv, exercise)
            await check_response(conv, Messages.EXERCISE_UNIT_REQUEST)
            await send_message(conv, unit)
            exp_msg_confirm = Messages.EXERCISE_CONFIRMATION.format(exercise_name=exercise, exercise_unit=unit)
            resp = await check_response(conv, exp_msg_confirm, buttons=approve_buttons)
            await click_button(resp, data="approve")

            exp_msg_added = Messages.EXERCISE_ADDED.format(exercise_name=exercise, unit=unit)
            await check_response(conv, exp_msg_added, edited=True)

        with step('Проверяем добавление упражнения в базу'):
            result = await db_session.execute(select(Exercise))
            db_exercise = result.scalars().one()

            assert db_exercise.name == exercise
            assert db_exercise.unit == unit

    @pytest.mark.parametrize('exercise', ["Упражнение1"])
    @title("Добавление нового упражнения с дефолтным измерением")
    async def test_added_new_exercise_with_default_unit(self, conversation, db_session, exercise, unit="раз"):

        async with conversation as conv:
            await send_message(conv, Commands.ADD_EXERCISE)
            await check_response(conv, Messages.EXERCISE_NAME_REQUEST)
            await send_message(conv, exercise)
            resp = await check_response(conv, Messages.EXERCISE_UNIT_REQUEST)
            await click_button(resp, data=unit)

            exp_msg_confirm = Messages.EXERCISE_CONFIRMATION.format(exercise_name=exercise, exercise_unit=unit)
            resp = await check_response(conv, exp_msg_confirm, edited=True, buttons=approve_buttons)
            await click_button(resp, data="approve")

            exp_msg_added = Messages.EXERCISE_ADDED.format(exercise_name=exercise, unit=unit)
            await check_response(conv, exp_msg_added, edited=True)

        with step('Проверяем добавление упражнения в базу'):
            result = await db_session.execute(select(Exercise))
            db_exercise = result.scalars().one()

            assert db_exercise.name == exercise
            assert db_exercise.unit == unit

    @title("Ошибка добавления существующего упражнения")
    async def test_existing_exercise_failed_add(self, conversation, db_session, new_exercise, unit="раз"):
        async with conversation as conv:
            await send_message(conv, Commands.ADD_EXERCISE)
            await check_response(conv, Messages.EXERCISE_NAME_REQUEST)
            await send_message(conv, new_exercise.name)
            resp = await check_response(conv, Messages.EXERCISE_UNIT_REQUEST)
            await click_button(resp, data=unit)

            exp_msg_confirm = Messages.EXERCISE_CONFIRMATION.format(exercise_name=new_exercise.name, exercise_unit=unit)
            resp = await check_response(conv, exp_msg_confirm, edited=True, buttons=approve_buttons)
            await click_button(resp, data="approve")

            exp_msg_added = Messages.EXERCISE_EXISTS.format(exercise_name=new_exercise.name)
            await check_response(conv, exp_msg_added, edited=True)
            await check_response(conv, Messages.EXERCISE_NAME_REQUEST)

        with step('Проверяем отсутствие дубля упражнения в базе'):
            result = await db_session.execute(select(Exercise))
            assert len(result.scalars().all()) == 1

    @pytest.mark.parametrize('exercise', ["Упражнение1"])
    @title("Добавление нового упражнения после ошибки дублирования")
    async def test_adding_exercise_after_failed_add(self, conversation, db_session, new_exercise, exercise, unit="раз"):
        async with conversation as conv:
            await send_message(conv, Commands.ADD_EXERCISE)
            await check_response(conv)
            await send_message(conv, new_exercise.name)
            resp = await check_response(conv)
            await click_button(resp, data=unit)
            resp = await check_response(conv, edited=True)
            await click_button(resp, data="approve")

            exp_msg_exists = Messages.EXERCISE_EXISTS.format(exercise_name=new_exercise.name)
            await check_response(conv, exp_msg_exists, edited=True)
            await check_response(conv, Messages.EXERCISE_NAME_REQUEST)

            await send_message(conv, exercise)
            resp = await check_response(conv)
            await click_button(resp, data=unit)
            resp = await check_response(conv, edited=True)
            await click_button(resp, data="approve")

            exp_msg_added = Messages.EXERCISE_ADDED.format(exercise_name=exercise, unit=unit)
            await check_response(conv, exp_msg_added, edited=True)

            with step('Проверяем добавление упражнения в базу'):
                result = await db_session.execute(select(Exercise))
                assert len(result.scalars().all()) == 2

    @pytest.mark.parametrize('exercise', ["Упражнение1"])
    @title("Отмена добавления упражнения")
    async def test_cancel_exercise_adding(self, conversation, exercise):
        async with conversation as conv:
            with step("Проверяем сброс при вводе команды на этапе названия"):
                await send_message(conv, Commands.ADD_EXERCISE)
                await check_response(conv, Messages.EXERCISE_NAME_REQUEST)
                await send_message(conv, Commands.ADD_EXERCISE)
                await check_response(conv, Messages.EXERCISE_NAME_REQUEST)
            with step("Проверяем сброс при вводе команды на этапе измерения"):
                await send_message(conv, exercise)
                await check_response(conv, Messages.EXERCISE_UNIT_REQUEST)
                await send_message(conv, Commands.ADD_EXERCISE)
                await check_response(conv, Messages.EXERCISE_NAME_REQUEST)
            with step("Проверяем сброс на этапе подтверждения по кнопке"):
                await send_message(conv, exercise)
                await check_response(conv, Messages.EXERCISE_UNIT_REQUEST)
                await send_message(conv, "раз")
                resp = await check_response(conv)
                await click_button(resp, data="cancel")
                await check_response(conv, Messages.EXERCISE_NAME_REQUEST)
