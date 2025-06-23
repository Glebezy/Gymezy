import asyncio
import pytest
from telethon import TelegramClient
import os
from dotenv import load_dotenv
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent
load_dotenv(f'{DATA_DIR}/.env.test')

bot_name = os.getenv('BOT_USERNAME')


@pytest.mark.asyncio
async def test_bot_response(client: TelegramClient):
    await client.connect()

    entity = await client.get_entity(bot_name)
    assert entity.username == bot_name

    async with client.conversation(bot_name) as conv:
        await conv.send_message('/start')
        response = await conv.get_response()
        assert 'Привет' in response.text
