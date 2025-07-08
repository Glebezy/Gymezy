from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select
from data.db import AsyncSessionLocal
from bot.utils.messages import Messages

from .states import WorkoutStates
from bot.utils.keyboards import exercise_list_keyboard, approve_keyboard, cancel_keyboard, add_exercise_keyboard, \
    start_workout_keyboard

router = Router()


@router.message(Command('start_workout'))
async def cmd_start_workout(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(telegram_id=message.from_user.id)
    await message.answer(Messages.WORKOUT_WELCOME_TEXT)
    await choose_exercise(message, state)


async def choose_exercise(message: Message, state: FSMContext):
    markup = await exercise_list_keyboard()

    if not markup.inline_keyboard:
        await message.answer(
            Messages.WORKOUT_EMPTY_EXERCISE,
            reply_markup=add_exercise_keyboard())
    else:
        await message.answer(
            Messages.WORKOUT_CHOOSE_EXERCISE,
            reply_markup=markup
        )
        await state.set_state(WorkoutStates.choosing_exercise)


@router.callback_query(F.data.startswith('exercise_'), WorkoutStates.choosing_exercise)
async def enter_value(callback: types.CallbackQuery, state: FSMContext):
    markup = cancel_keyboard()
    await state.update_data(chosen_exercise=callback.data.split('_')[1])
    await state.update_data(chosen_exercise_id=callback.data.split('_')[2])
    await state.update_data(chosen_exercise_unit=callback.data.split('_')[3])
    data = await state.get_data()
    await state.set_state(WorkoutStates.entering_value)

    await callback.message.edit_text(Messages.WORKOUT_EXERCISE_VALUE.format(unit=data['chosen_exercise_unit']),
                                     reply_markup=markup
                                     )


@router.message(F.text.regexp(r'\d'), WorkoutStates.entering_value)
async def approve_exercise(message: Message, state: FSMContext):
    await state.update_data(chosen_exercise_value=message.text.lower())

    data = await state.get_data()

    await message.answer(Messages.WORKOUT_EXERCISE_CONFIRMATION.format(exercise=data['chosen_exercise'],
                                                                       value=data['chosen_exercise_value'],
                                                                       unit=data['chosen_exercise_unit']),
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
        await state.set_state(WorkoutStates.saving_exercise)
        await callback.message.edit_text(
            Messages.WORKOUT_EXERCISE_ADDED.format(exercise=data['chosen_exercise'],
                                                   value=data['chosen_exercise_value'],
                                                   unit=data['chosen_exercise_unit']),
            reply_markup=start_workout_keyboard()
        )


@router.callback_query(F.data == 'cancel', WorkoutStates.entering_value)
async def cancel_exercise(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await choose_exercise(callback.message, state)


@router.callback_query(F.data == 'cancel', WorkoutStates.saving_exercise)
async def cancel_workout(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


@router.callback_query(F.data == 'start_workout')
async def return_to_start_workout(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await choose_exercise(callback.message, state)
