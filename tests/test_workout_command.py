import allure
import pytest
from sqlalchemy import select
from bot.utils.commands import Commands
from bot.utils.messages import Messages
from data.models import Exercise, Workout
from .utils import check_response, send_message, click_button
from allure import step, title

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
@allure.story('Workout Commands')
class TestWorkoutCommand:

    @title("Запуск тренировки без упражнений")
    async def test_workout_command_without_exercise(self, conversation):
        async with conversation as conv:
            await send_message(conv, Commands.START_WORKOUT)
            await check_response(conv, Messages.WORKOUT_WELCOME_TEXT)
            await check_response(conv, Messages.WORKOUT_EMPTY_EXERCISE, exercise_buttons)

    @title("Создания упражнения из формы тренировки")
    @pytest.mark.parametrize('exercise_name, exercise_unit', [("Присед", "раз")])
    async def test_create_exercise_with_default_unit_from_workout(self, conversation, db_session, exercise_name, exercise_unit):
        async with conversation as conv:
            await send_message(conv, Commands.START_WORKOUT)

            resp = await check_response(conv, count=2)
            await click_button(resp, "add_exercise")

            await check_response(conv, Messages.EXERCISE_NAME_REQUEST)

            await send_message(conv, exercise_name)
            resp = await check_response(conv, Messages.EXERCISE_UNIT_REQUEST)
            await click_button(resp, data=exercise_unit)

            exp_msg_confirm = Messages.EXERCISE_CONFIRMATION.format(exercise_name=exercise_name, exercise_unit=exercise_unit)
            resp = await check_response(conv, exp_msg_confirm, edited=True, buttons=approve_buttons)
            await click_button(resp, data="approve")

            exp_msg_added = Messages.EXERCISE_ADDED.format(exercise_name=exercise_name, unit=exercise_unit)
            await check_response(conv, exp_msg_added, edited=True)

            result = await db_session.execute(select(Exercise))
            db_exercise = result.scalars().one()

            assert db_exercise.name == exercise_name
            assert db_exercise.unit == exercise_unit

            callback_data = f"exercise_{db_exercise.name}_{db_exercise.id}_{db_exercise.unit}"

            exercise_buttons = [{
                "text": exercise_name,
                "data": bytes(callback_data, 'utf-8')
            }]

            await send_message(conv, Commands.START_WORKOUT)
            await check_response(conv, Messages.WORKOUT_WELCOME_TEXT)
            await check_response(conv, Messages.WORKOUT_CHOOSE_EXERCISE, buttons=exercise_buttons)

    @title("Создание тренировки")
    async def test_create_workout(self, conversation, new_user, new_exercise, db_session):
        with step('Проверяем пустую таблицу тренировок'):
            result = await db_session.execute(select(Workout))
            assert len(result.scalars().all()) == 0

        async with conversation as conv:
            await send_message(conv, Commands.START_WORKOUT)
            await check_response(conv, Messages.WORKOUT_WELCOME_TEXT)

            resp = await check_response(conv, Messages.WORKOUT_CHOOSE_EXERCISE)
            await click_button(resp, text=new_exercise.name)

            await check_response(conv, Messages.WORKOUT_EXERCISE_VALUE.format(unit=new_exercise.unit), edited=True)
            await send_message(conv, '15')
            resp = await check_response(conv, Messages.WORKOUT_EXERCISE_CONFIRMATION.format(
                exercise=new_exercise.name,
                value=15,
                unit=new_exercise.unit
            ), buttons=approve_buttons)
            await click_button(resp, data="approve")
            await check_response(conv, Messages.WORKOUT_EXERCISE_ADDED.format(
                exercise=new_exercise.name,
                value=15,
                unit=new_exercise.unit
            ), edited=True)

            with step('Проверяем добавление тренировки в базу'):
                result = await db_session.execute(select(Workout))
                db_workout = result.scalars().one()

                assert db_workout.exercise_id == new_exercise.id
                assert db_workout.user_id == new_user.id
                assert db_workout.value == 15


