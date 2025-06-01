from aiogram import types
from data.db import AsyncSessionLocal
from sqlalchemy import select
from data.models import User


async def start_command(message: types.Message):
    db = AsyncSessionLocal()

    async with db as session:
        result = await session.execute(
            select(User.id).filter_by(telegram_id=message.from_user.id)
        )
        user = result.scalar_one_or_none()  # Важно!

        if user is None:
            # Регистрируем нового пользователя
            new_user = User(
                telegram_id=message.from_user.id,
                name=message.from_user.first_name,
                username=message.from_user.username
            )
            session.add(new_user)
            await session.commit()
            await message.answer(
                "🎉 Добро пожаловать в GymezyBot!\n"
                "Я помогу тебе отслеживать твои тренировки."
            )
        else:
            await message.answer("С возвращением! 🏋️")
