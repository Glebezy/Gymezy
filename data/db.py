import asyncio
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from data.models import Base
from dotenv import load_dotenv


env = os.getenv('ENV', 'prod')  # По умолчанию 'test'
load_dotenv(f'.env.{env}')


DATA_DIR = Path(__file__).parent / "database"
DATA_DIR.mkdir(exist_ok=True)
DB_NAME = os.getenv("DB_NAME")
DB_PATH = DATA_DIR / DB_NAME

DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DB_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
