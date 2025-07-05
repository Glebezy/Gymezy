from aiogram import types, Router
from sqlalchemy.ext.asyncio import AsyncSession
from .stats import print_daily_stats
from aiogram.filters import Command
from data.db import AsyncSessionLocal
from sqlalchemy import select
from data.models import User
from .messages import Messages

router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message):
    db = AsyncSessionLocal()

    async with db as session:
        result = await session.execute(
            select(User).filter_by(telegram_id=message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            await registration_user(message, session)
        else:
            await message.answer(Messages.LOGIN_TEXT.format(user_name=user.name))
            await print_daily_stats(message)


async def registration_user(message: types.Message, session: AsyncSession):
    new_user = User(
        telegram_id=message.from_user.id,
        name=message.from_user.first_name,
        username=message.from_user.username
    )
    session.add(new_user)
    await session.commit()
    await message.answer(Messages.WELCOME_TEXT)
