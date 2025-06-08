from sqlalchemy import Integer, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, declared_attr
from sqlalchemy.orm import mapped_column
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[int] = mapped_column(default=lambda: int(datetime.now().timestamp()))
    updated_at: Mapped[int] = mapped_column(default=lambda: int(datetime.now().timestamp()),
                                            onupdate=lambda: int(datetime.now().timestamp()))

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'


class User(Base):
    telegram_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str]
    username: Mapped[str]


class Exercise(Base):
    name: Mapped[str] = mapped_column(unique=True)
    unit: Mapped[str] = mapped_column(nullable=False)


class Workout(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    exercise_id: Mapped[int] = mapped_column(ForeignKey('exercises.id'))
    value: Mapped[int]
