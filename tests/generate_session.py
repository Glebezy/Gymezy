from pathlib import Path
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os
from dotenv import load_dotenv
import asyncio

DATA_DIR = Path(__file__).parent.parent
load_dotenv(f'{DATA_DIR}/.env.test')

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')


async def generate_session():
    client = TelegramClient(StringSession(), api_id, api_hash)

    client.session.set_dc(2, '149.154.167.40', 80)

    await client.connect()

    if not await client.is_user_authorized():
        phone = input("Введите номер телефона (с кодом страны): ")
        await client.send_code_request(phone)

        code = input("Введите код подтверждения: ")
        await client.sign_in(phone=phone, code=code)

    session_string = client.session.save()
    print(f"\nВаша session string (сохранена в .env.test):\n{session_string}")

    # Автоматическое сохранение в .env.test
    with open('../.env.test', 'a') as f:
        f.write(f"\nSESSION_STRING={session_string}")

    await client.disconnect()


if __name__ == '__main__':
    asyncio.run(generate_session())
