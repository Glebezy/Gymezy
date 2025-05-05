from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent / "database"
DATA_DIR.mkdir(exist_ok=True)
DB_NAME = os.getenv("DB_NAME")
DB_PATH = DATA_DIR / DB_NAME

DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, echo="debug")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_db_and_tables() -> None:
    Base.metadata.create_all(engine)


with SessionLocal() as session:
    try:
        create_db_and_tables()
    except Exception as e:
        session.rollback()
        raise e
    else:
        session.commit()
