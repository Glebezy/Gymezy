from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from bot.utils.messages import Messages
from .states import ExerciseStates
from bot.utils.keyboards import choose_exercise_value_keyboard, approve_keyboard

router = Router()


@router.message(Command("add_exercise"))
async def cmd_add_exercise(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(Messages.EXERCISE_NAME_REQUEST)
    await state.set_state(ExerciseStates.waiting_for_exercise_name)


@router.callback_query(F.data == "add_exercise")
async def cmd_add_exercise_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(Messages.EXERCISE_NAME_REQUEST)
    await state.set_state(ExerciseStates.waiting_for_exercise_name)


@router.message(ExerciseStates.waiting_for_exercise_name, F.text.not_contains("/"))
async def process_exercise_name(message: Message, state: FSMContext):
    await state.update_data(exercise_name=message.text.capitalize())

    await message.answer(
        Messages.EXERCISE_UNIT_REQUEST,
        reply_markup=choose_exercise_value_keyboard()
    )
    await state.set_state(ExerciseStates.waiting_for_exercise_unit)


@router.message(ExerciseStates.waiting_for_exercise_unit, F.text.not_contains("/"))
async def process_exercise_unit_message(message: Message, state: FSMContext):
    await state.update_data(exercise_unit=message.text)
    data = await state.get_data()

    await message.answer(
        Messages.EXERCISE_CONFIRMATION.format(exercise_name=data['exercise_name'], exercise_unit=data['exercise_unit']),
        reply_markup=approve_keyboard()
    )
    await state.set_state(ExerciseStates.waiting_for_exercise_approve)


@router.callback_query(ExerciseStates.waiting_for_exercise_unit)
async def process_exercise_unit_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(exercise_unit=callback.data)
    data = await state.get_data()

    await callback.message.edit_text(
        Messages.EXERCISE_CONFIRMATION.format(exercise_name=data['exercise_name'], exercise_unit=data['exercise_unit']),
        reply_markup=approve_keyboard()
    )
    await state.set_state(ExerciseStates.waiting_for_exercise_approve)


@router.callback_query(ExerciseStates.waiting_for_exercise_approve)
async def process_exercise_approve(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == "approve":
        data = await state.get_data()
        exercise_name = data['exercise_name']
        unit = data['exercise_unit']

        from data.models import Exercise
        from data.db import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Exercise).where(Exercise.name == exercise_name)
            )
            exercise = result.scalars().first()
            if exercise is None:
                new_exercise = Exercise(
                    name=exercise_name,
                    unit=unit
                )
                session.add(new_exercise)
                await session.commit()
                await callback.message.edit_text(
                    Messages.EXERCISE_ADDED.format(exercise_name=data['exercise_name'], unit=unit),
                )
            else:
                await callback.message.edit_text(
                    Messages.EXERCISE_EXISTS.format(exercise_name=data['exercise_name'])
                )
    else:
        await callback.message.edit_text(Messages.ADD_EXERCISE_COMMAND)
    await state.clear()
