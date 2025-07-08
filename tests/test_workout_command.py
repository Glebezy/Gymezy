import pytest
from sqlalchemy import select
from bot.utils.commands import Commands
from bot.utils.messages import Messages
from data.models import Exercise
from .utils import check_response

exercise_buttons = [{
        "text": 'Добавить упражнение',
        "data": b'add_exercise'
    }]

approve_buttons = [{
            "text": 'Подтвердить',
            "data": b'approve'
        }, {
            "text": 'Отмена',
            "data": b'cancel'
        }]


@pytest.mark.asyncio
async def test_workout_command_without_exercise(bot_conversation):
    async with bot_conversation as conv:
        await conv.send_message(Commands.START_WORKOUT)
        await check_response(conv, Messages.WORKOUT_WELCOME_TEXT)
        await check_response(conv, Messages.WORKOUT_EMPTY_EXERCISE, exercise_buttons)


@pytest.mark.parametrize('exercise_name, exercise_unit', [("Присед", "раз")])
@pytest.mark.asyncio
async def test_create_exercise_with_default_unit_from_workout(bot_conversation, db_session, exercise_name, exercise_unit):
    async with bot_conversation as conv:
        await conv.send_message(Commands.START_WORKOUT)

        resp = await check_response(conv, count=2)
        await resp.click(data="add_exercise")

        await check_response(conv, Messages.EXERCISE_NAME_REQUEST)

        await conv.send_message(exercise_name)
        resp = await check_response(conv, Messages.EXERCISE_UNIT_REQUEST)
        await resp.click(data="раз")

        exp_msg_confirm = Messages.EXERCISE_CONFIRMATION.format(exercise_name=exercise_name, exercise_unit=exercise_unit)
        resp = await check_response(conv, exp_msg_confirm, edited=True, buttons=approve_buttons)
        await resp.click(data="approve")

        exp_msg_added = Messages.EXERCISE_ADDED.format(exercise_name=exercise_name, unit=exercise_unit)
        await check_response(conv, exp_msg_added, edited=True)

        result = await db_session.execute(select(Exercise))
        db_exercise = result.scalars().one()

        assert db_exercise.name == exercise_name.lower()
        assert db_exercise.unit == exercise_unit
