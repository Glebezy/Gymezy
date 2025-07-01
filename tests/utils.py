import asyncio

from telethon import TelegramClient


async def check_answer(client: TelegramClient, entity, exp_message_text, message_count=1):
    await asyncio.sleep(1.5)
    response = await client.get_messages(entity, message_count)
    assert any(exp_message_text in item.message for item in response)
