from allure_commons._allure import step
from telethon.tl.custom import Conversation


@step("Проверяем ответ от бота")
async def check_response(conv: Conversation, exp_message_text=None, buttons=None, count=1, edited=False):
    if edited:
        msg = await conv.get_edit()
    else:
        for _ in range(count):
            msg = await conv.get_response()

    if exp_message_text is None:
        return msg

    with step(f"Проверяем текст сообщения"):
        assert msg.message == exp_message_text, f'Текст сообщения не совпадает {msg.message} != {exp_message_text}'

    if buttons is not None:
        with step(f'Проверяем примыкающую клавиатуру'):

            markup_buttons = []
            for row in msg.reply_markup.rows:
                markup_buttons.extend(row.buttons)

            assert len(markup_buttons) == len(buttons), (
                f"Количество кнопок не совпадает: {len(markup_buttons)} != {len(buttons)}"
            )

            for markup_button, expected_button in zip(markup_buttons, buttons):
                assert markup_button.text == expected_button['text'], (
                    f"Текст кнопки не совпадает: '{markup_button.text}' != '{expected_button['text']}'"
                )
                assert markup_button.data == expected_button['data'], (
                    f"Данные кнопки не совпадают: '{markup_button.data}' != '{expected_button['data']}'"
                )

    return msg


@step("Отправляем боту сообщение '{message}'")
async def send_message(conv: Conversation, message):
    await conv.send_message(message)


@step("Нажимаем на кнопку {data} или {text}")
async def click_button(message, data=None, text=None):
    await message.click(data=data, text=text)
