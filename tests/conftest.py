import pytest
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
from dotenv import load_dotenv
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent
load_dotenv(f'{DATA_DIR}/.env.test')


@pytest.fixture(scope='session')
@pytest.mark.asyncio
def client() -> TelegramClient:
    client = TelegramClient(
        StringSession(os.getenv('SESSION_STRING')),
        os.getenv('API_ID'),
        os.getenv('API_HASH')
    )

    client.session.set_dc(2, '149.154.167.40', 80)

    return client
