from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from .states import ExerciseStates

router = Router()


@router.message(Command("add_exercise"))
async def cmd_add_exercise(message: Message, state: FSMContext):
    await message.answer(
        "Введите название упражнения (например, \"Жим лежа\"):"
    )
    await state.set_state(ExerciseStates.waiting_for_exercise_name)


@router.message(ExerciseStates.waiting_for_exercise_name)
async def process_exercise_name(message: Message, state: FSMContext):
    # Сохраняем название упражнения
    await state.update_data(exercise_name=message.text)

    await message.answer(
        "Введите единицы измерения (например, \"кг\" или \"раз\"):"
    )
    await state.set_state(ExerciseStates.waiting_for_exercise_unit)


@router.message(ExerciseStates.waiting_for_exercise_unit)
async def process_exercise_unit(message: Message, state: FSMContext):
    # Сохраняем название упражнения
    await state.update_data(exercise_unit=message.text)
    data = await state.get_data()

    await message.answer(
        f"Вы добавляете упражнение \"{data['exercise_name']}\" в измерении \"{data['exercise_unit']}\""
    )
    await message.answer(f"Напишите \"Да\" если все верно")
    await state.set_state(ExerciseStates.waiting_for_exercise_approve)


@router.message(ExerciseStates.waiting_for_exercise_approve)
async def process_exercise_approve(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        # Получаем сохраненные данные
        data = await state.get_data()
        exercise_name = data['exercise_name'].lower()
        unit = data['exercise_unit']

        # Здесь сохраняем упражнение в БД
        # Пример (реализуйте свою логику сохранения):
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
                await message.answer(
                    f"Упражнение \"{data['exercise_name']}\" ({unit}) успешно добавлено!"
                )
            else:
                await message.answer(
                    f"Упражнение \"{data['exercise_name']}\" уже существует!"
                )
    else:
        await message.answer("Для добавления упражнения введите /add_exercise")
    await state.clear()
