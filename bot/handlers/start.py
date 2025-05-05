from aiogram import types
from data.db import SessionLocal
from data.models import User


async def start_command(message: types.Message):
    db = SessionLocal()

    try:
        # Проверяем, зарегистрирован ли пользователь
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()

        if not user:
            # Регистрируем нового пользователя
            new_user = User(
                telegram_id=message.from_user.id,
                name=message.from_user.first_name,
                username=message.from_user.username
            )
            db.add(new_user)
            db.commit()
            await message.answer(
                "🎉 Добро пожаловать в GymezyBot!\n"
                "Я помогу тебе отслеживать твои тренировки."
            )
        else:
            await message.answer("С возвращением! 🏋️")

    except Exception as e:
        db.rollback()
        print(f"Ошибка при регистрации: {e}")
        await message.answer("Произошла ошибка")
    finally:
        db.close()
