from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select
from data.db import AsyncSessionLocal

from .states import WorkoutStates
from ..keyboards import exercise_list_keyboard, approve_keyboard, cancel_keyboard

router = Router()


@router.message(Command('start_workout'))
async def cmd_start_workout(message: Message, state: FSMContext):
    await state.update_data(telegram_id=message.from_user.id)
    await choose_exercise(message, state)


async def choose_exercise(message: Message, state: FSMContext):
    welcome_text = "Приветствую на форме создания тренировки \n"
    markup = await exercise_list_keyboard()
    if not markup.inline_keyboard:

        await message.answer(f"{welcome_text} Извините, в данный момент нет доступных упражнений.")
    else:
        await message.answer(
            f"{welcome_text}Выберите упражнение",
            reply_markup=markup
        )
        await state.set_state(WorkoutStates.choosing_exercise)


@router.callback_query(F.data.startswith('exercise_'), WorkoutStates.choosing_exercise)
async def enter_value(callback: types.CallbackQuery, state: FSMContext):
    markup = cancel_keyboard()
    await state.update_data(chosen_exercise=callback.data.split('_')[1])
    await state.update_data(chosen_exercise_id=callback.data.split('_')[2])
    await state.set_state(WorkoutStates.entering_value)

    await callback.message.edit_text(text="Введите кол-во выполненных раз",
                                     reply_markup=markup
                                     )


@router.message(F.text.regexp(r'\d'), WorkoutStates.entering_value)
async def approve_exercise(message: Message, state: FSMContext):
    await state.update_data(chosen_exercise_value=message.text.lower())

    data = await state.get_data()

    await message.answer(
        f"Вы сохраняете упражнение \"{data['chosen_exercise']}\" в кол-ве \"{data['chosen_exercise_value']}\" раз",
        reply_markup=approve_keyboard()
    )


@router.callback_query(F.data == 'approve', WorkoutStates.entering_value)
async def save_exercise(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    exercise_id = data['chosen_exercise_id']
    value = data['chosen_exercise_value']
    telegram_id = data['telegram_id']

    from data.models import Workout, User

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User.id).filter(User.telegram_id == telegram_id)
        )
        user_id = result.scalars().one()

        new_workout = Workout(
            exercise_id=exercise_id,
            value=value,
            user_id=user_id
        )
        session.add(new_workout)
        await session.commit()
        await callback.message.edit_text(
            f"Упражнение \"{data['chosen_exercise']}\" ({value}) успешно зафиксировано!"
        )
    await choose_exercise(callback.message, state)


@router.callback_query(F.data == 'cancel', WorkoutStates.entering_value)
async def cancel_exercise(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await choose_exercise(callback.message, state)
