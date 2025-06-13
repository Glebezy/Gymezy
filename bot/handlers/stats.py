from datetime import datetime, time
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from data.db import AsyncSessionLocal
from data.models import Workout, User, Exercise

router = Router()


@router.message(Command("daily_stats"))
async def cmd_stats(message: Message):
    daily_workouts = await get_daily_stats(message.from_user.id)

    if not daily_workouts:
        await message.answer("За сегодня тренировок нет")
        return

    i = 1
    report = ["🏋️ Ваши тренировки за сегодня:\n"]
    for workout in daily_workouts:
        dt = datetime.fromtimestamp(workout.created_at)
        report.append(
            f"{i}. {workout.name.capitalize()} {workout.value} раз в {dt.strftime('%H:%M')}"
        )
        i += 1

    await message.answer("\n".join(report))


async def get_daily_stats(telegram_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User.id).filter(User.telegram_id == telegram_id)
        )
        user_id = result.scalars().one()

        now = datetime.now()
        start_of_day = datetime.combine(now.date(), time.min)
        start_of_day_timestamp = int(start_of_day.timestamp())

        query = select(Exercise.name, Workout.value, Workout.created_at
                       ).join(Exercise,Exercise.id == Workout.exercise_id).where(
            Workout.user_id == user_id,
            Workout.created_at >= start_of_day_timestamp
        ).order_by(Workout.created_at.desc())

        result = await session.execute(query)
        return result.all()
