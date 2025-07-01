import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from data.models import Base
from dotenv import load_dotenv


def _init_db(env: str):
    main_dir = Path(__file__).parent.parent
    load_dotenv(f'{main_dir}/.env.{env}')

    db_path = main_dir / "data/databases" / os.getenv("DB_NAME")
    db_path.parent.mkdir(exist_ok=True)

    return create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        echo=False
    )


_engine = None


def _get_engine(env: str):
    global _engine
    if _engine is None:
        _engine = _init_db(env)
    return _engine


AsyncSessionLocal = async_sessionmaker(_get_engine(os.getenv('ENV')), expire_on_commit=False, class_=AsyncSession)


async def create_db(env: str):
    engine = _get_engine(env)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
