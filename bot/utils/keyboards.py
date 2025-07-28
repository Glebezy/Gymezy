from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select


async def exercise_list_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    from data.models import Exercise
    from data.db import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Exercise))
        exercises = result.scalars().all()

        if exercises:
            for exercise in exercises:
                builder.button(text=exercise.name, callback_data=f"exercise_{exercise.name}_{exercise.id}_{exercise.unit}")

    builder.adjust(2)

    return builder.as_markup()


def add_exercise_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='Добавить упражнение', callback_data='add_exercise')
    return builder.as_markup()


def start_workout_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='Продолжить тренировку', callback_data='start_workout')
    builder.attach(InlineKeyboardBuilder.from_markup(cancel_keyboard()))
    return builder.as_markup()


def choose_exercise_value_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Оставить без изменений', callback_data='раз')
    return kb.as_markup()


def approve_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Подтвердить", callback_data='approve')
    kb.attach(InlineKeyboardBuilder.from_markup(cancel_keyboard()))
    kb.adjust(2)
    return kb.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена", callback_data='cancel')
    return kb.as_markup()


def stats_date_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Вчера", callback_data='1_stats')
    kb.button(text="Неделя", callback_data='7_stats')
    kb.button(text="Месяц", callback_data='30_stats')
    kb.button(text="Квартал", callback_data='90_stats')
    kb.button(text="Полгода", callback_data='180_stats')
    kb.button(text="Год", callback_data='365_stats')
    kb.button(text="Все время", callback_data='total_stats')

    kb.adjust(2)
    return kb.as_markup()
