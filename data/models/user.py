from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, auto_increment=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str]
    username: Mapped[str]
    created_at: Mapped[int] = mapped_column(default=lambda: int(datetime.now().timestamp()))
